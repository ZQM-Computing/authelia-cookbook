"""Smoke-test the disposable Caddy/Authelia proxy fixture.

This tests public routing, unauthenticated denial, unknown hosts, spoofed
identity headers, and host-port exposure. It does not yet establish a valid
Authelia browser session, so it is not full authorization coverage.
"""
from http.client import HTTPConnection, HTTPSConnection
import json
from pathlib import Path
import re
import socket
import ssl
import subprocess
import time
import unittest

ROOT = Path(__file__).parent
DENIAL_STATUSES = {302, 401, 403}


class SNIHTTPSConnection(HTTPSConnection):
    """Connect to loopback while using the requested virtual host for TLS SNI."""

    def __init__(self, server_name: str, port: int, timeout: int = 5):
        self.server_name = server_name
        super().__init__("127.0.0.1", port, timeout=timeout, context=ssl._create_unverified_context())

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.server_name)


def request(host: str, headers: dict[str, str] | None = None, *, secure: bool = False):
    if secure:
        connection = SNIHTTPSConnection(host, 18443)
        port = 18443
    else:
        connection = HTTPConnection("127.0.0.1", 18080, timeout=5)
        port = 18080
    try:
        connection.request("GET", "/", headers={"Host": host, **(headers or {})})
        response = connection.getresponse()
        return response.status, response.read().decode("utf-8", errors="replace")
    finally:
        connection.close()


class ProxyIntegrationSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        last_result = "no HTTP response"
        for attempt in range(15):
            try:
                status, body = request("public.example.test")
                last_result = f"HTTP {status}: {body[:300]!r}"
                if status == 200 and "PUBLIC_UPSTREAM_MARKER" in body:
                    break
            except OSError as exc:
                last_result = repr(exc)
            time.sleep(1)
        else:
            raise RuntimeError(f"Caddy fixture did not return the public marker; last result: {last_result}")

        last_result = "no HTTPS response"
        for attempt in range(15):
            try:
                status, body = request("protected.example.test", secure=True)
                last_result = f"HTTPS {status}: {body[:300]!r}"
                if status in DENIAL_STATUSES:
                    return
            except OSError as exc:
                last_result = repr(exc)
            time.sleep(1)
        raise RuntimeError(f"HTTPS protected route did not become ready; last result: {last_result}")

    def test_public_host_reaches_only_public_marker(self):
        status, body = request("public.example.test")
        self.assertEqual(status, 200)
        self.assertIn("PUBLIC_UPSTREAM_MARKER", body)
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_protected_host_denies_request_without_session(self):
        status, body = request("protected.example.test", secure=True)
        self.assertIn(status, DENIAL_STATUSES, f"Expected denial/redirect, got {status}: {body}")
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_client_cannot_spoof_identity_headers_to_bypass_auth(self):
        status, body = request(
            "protected.example.test",
            {
                "Remote-User": "spoofed-user",
                "Remote-Groups": "admins",
                "Remote-Name": "Spoofed Identity",
                "Remote-Email": "spoofed@example.test",
            },
            secure=True,
        )
        self.assertIn(status, DENIAL_STATUSES, f"Identity spoofing bypassed authorization: {status}: {body}")
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_unknown_host_returns_404_without_upstream_marker(self):
        status, body = request("unknown.example.test")
        self.assertEqual(status, 404, body)
        self.assertNotIn("PUBLIC_UPSTREAM_MARKER", body)
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_only_loopback_caddy_listeners_are_published(self):
        rendered = subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "config", "--format", "json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        config = json.loads(rendered.stdout)
        published = []
        for service_name, service in config["services"].items():
            for port in service.get("ports", []):
                published.append((service_name, port.get("host_ip"), str(port.get("published")), str(port.get("target"))))
        self.assertEqual(
            published,
            [
                ("caddy", "127.0.0.1", "18080", "8080"),
                ("caddy", "127.0.0.1", "18443", "8443"),
            ],
        )

    def test_forward_auth_directive_is_required(self):
        # Regression guard: removing forward_auth must fail CI even if a
        # particular request happens to receive a denial for another reason.
        caddyfile = (ROOT / "Caddyfile").read_text()
        protected_site = re.search(
            r"https://protected\.example\.test:8443\s*\{(.*?)\n\}",
            caddyfile,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(protected_site, "Protected virtual host definition is missing")
        self.assertRegex(
            protected_site.group(1),
            r"(?m)^\s*forward_auth\s+authelia:9091\s*\{",
            "Protected route must enforce Authelia forward_auth",
        )
        self.assertRegex(
            protected_site.group(1),
            r"(?m)^\s*uri\s+/api/authz/forward-auth\s*$",
            "Protected route must use Authelia's forward-auth endpoint",
        )

    def test_protected_upstream_must_not_publish_host_ports(self):
        # Regression guard: publishing protected-app directly would create an
        # authorization bypass around Caddy and must fail CI.
        rendered = subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "config", "--format", "json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        config = json.loads(rendered.stdout)
        protected = config["services"]["protected-app"]
        self.assertFalse(
            protected.get("ports"),
            "Protected upstream must not publish any host ports",
        )
        self.assertFalse(
            config["services"]["authelia"].get("ports"),
            "Authelia must not publish any host ports in this fixture",
        )

    def test_private_network_is_internal(self):
        rendered = subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "config", "--format", "json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        config = json.loads(rendered.stdout)
        self.assertTrue(config["networks"]["proxy-test"]["internal"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
