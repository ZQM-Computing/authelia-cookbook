"""Smoke-test the disposable Caddy/Authelia proxy fixture.

This tests public routing, unauthenticated denial, unknown hosts, spoofed
identity headers, and host-port exposure. It does not yet establish a valid
Authelia browser session, so it is not full authorization coverage.
"""
from http.client import HTTPConnection, HTTPSConnection
import json
import os
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


def assert_forward_auth_contract(caddyfile: str) -> None:
    protected_site = re.search(
        r"https://protected\\.example\\.test:8443\\s*\\{(.*?)\\n\\}",
        caddyfile,
        flags=re.DOTALL,
    )
    assert protected_site is not None, "Protected virtual host definition is missing"
    assert re.search(
        r"(?m)^\\s*forward_auth\\s+authelia:9091\\s*\\{",
        protected_site.group(1),
    ), "Protected route must enforce Authelia forward_auth"
    assert re.search(
        r"(?m)^\\s*uri\\s+/api/authz/forward-auth\\s*$",
        protected_site.group(1),
    ), "Protected route must use Authelia's forward-auth endpoint"


def assert_upstreams_unpublished(config: dict) -> None:
    services = config["services"]
    assert not services["protected-app"].get("ports"), (
        "Protected upstream must not publish any host ports"
    )
    assert not services["authelia"].get("ports"), (
        "Authelia must not publish any host ports in this fixture"
    )


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

    def test_valid_session_reaches_upstream_with_verified_identity(self):
        password_file = os.environ.get("DEMO_PASSWORD_FILE")
        self.assertTrue(password_file, "CI must provide a path to the throwaway demo password")
        password = Path(password_file).read_text(encoding="utf-8").strip()
        self.assertTrue(password, "Throwaway demo password file must not be empty")

        payload = json.dumps({
            "username": "demo",
            "password": password,
            "keepMeLoggedIn": False,
            "targetURL": "https://protected.example.test:18443/",
        })
        connection = SNIHTTPSConnection("auth.example.test", 18443)
        try:
            connection.request(
                "POST",
                "/api/firstfactor",
                body=payload,
                headers={
                    "Host": "auth.example.test",
                    "Content-Type": "application/json",
                    "Origin": "https://auth.example.test:18443",
                    "Referer": "https://auth.example.test:18443/",
                },
            )
            login = connection.getresponse()
            login_body = login.read().decode("utf-8", errors="replace")
            self.assertEqual(login.status, 200, f"Authelia first-factor login failed: {login_body}")
            set_cookie = login.getheader("Set-Cookie")
            self.assertTrue(set_cookie, f"Successful login did not set a session cookie: {login_body}")
            cookie = set_cookie.split(";", 1)[0]
            self.assertIn("=", cookie)
        finally:
            connection.close()

        status, body = request(
            "protected.example.test",
            {
                "Cookie": cookie,
                "Remote-User": "spoofed-user",
                "Remote-Groups": "admins",
                "Remote-Name": "Spoofed Identity",
                "Remote-Email": "spoofed@example.test",
            },
            secure=True,
        )
        self.assertEqual(status, 200, f"Authenticated session did not reach upstream: {body}")
        self.assertIn("PROTECTED_UPSTREAM_MARKER", body)
        marker, separator, identity_json = body.partition("\n")
        self.assertEqual(marker, "PROTECTED_UPSTREAM_MARKER")
        self.assertTrue(separator, f"Protected upstream omitted its identity payload: {body!r}")
        identity = json.loads(identity_json.strip())
        self.assertEqual(identity["Remote-User"], "demo")
        self.assertEqual(identity["Remote-Groups"], "demo-users")
        self.assertEqual(identity["Remote-Name"], "Demo User")
        self.assertEqual(identity["Remote-Email"], "demo@example.test")

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
        assert_forward_auth_contract((ROOT / "Caddyfile").read_text())

    def test_forward_auth_guard_rejects_removed_directive(self):
        caddyfile = (ROOT / "Caddyfile").read_text()
        mutated = re.sub(
            r"(?m)^\\s*forward_auth\\s+authelia:9091\\s*\\{\\s*$",
            "",
            caddyfile,
        )
        with self.assertRaisesRegex(AssertionError, "forward_auth"):
            assert_forward_auth_contract(mutated)

    def test_protected_upstream_must_not_publish_host_ports(self):
        rendered = subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "config", "--format", "json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert_upstreams_unpublished(json.loads(rendered.stdout))

    def test_port_exposure_guard_rejects_published_protected_upstream(self):
        rendered = subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "config", "--format", "json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        config = json.loads(rendered.stdout)
        mutated = json.loads(json.dumps(config))
        mutated["services"]["protected-app"]["ports"] = [
            {"host_ip": "0.0.0.0", "published": "18081", "target": 80}
        ]
        with self.assertRaisesRegex(AssertionError, "Protected upstream"):
            assert_upstreams_unpublished(mutated)

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
