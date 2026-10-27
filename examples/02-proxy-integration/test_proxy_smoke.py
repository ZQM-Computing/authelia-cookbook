"""Smoke-test the disposable Caddy/Authelia proxy fixture.

This intentionally tests public routing, unauthenticated denial, unknown hosts,
spoofed identity headers, and host-port exposure. It does not yet establish a
valid Authelia browser session, so it is not full authorization coverage.
"""
from http.client import HTTPConnection
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).parent
DENIAL_STATUSES = {302, 401, 403}


def request(host: str, headers: dict[str, str] | None = None):
    connection = HTTPConnection("127.0.0.1", 18080, timeout=5)
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
                    return
            except OSError as exc:
                last_result = repr(exc)
            import time
            time.sleep(1)
        raise RuntimeError(f"Caddy fixture did not return the public marker; last result: {last_result}")

    def test_public_host_reaches_only_public_marker(self):
        status, body = request("public.example.test")
        self.assertEqual(status, 200)
        self.assertIn("PUBLIC_UPSTREAM_MARKER", body)
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_protected_host_denies_request_without_session(self):
        status, body = request("protected.example.test")
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
        )
        self.assertIn(status, DENIAL_STATUSES, f"Identity spoofing bypassed authorization: {status}: {body}")
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_unknown_host_returns_404_without_upstream_marker(self):
        status, body = request("unknown.example.test")
        self.assertEqual(status, 404, body)
        self.assertNotIn("PUBLIC_UPSTREAM_MARKER", body)
        self.assertNotIn("PROTECTED_UPSTREAM_MARKER", body)

    def test_only_loopback_caddy_listener_is_published(self):
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
        self.assertEqual(published, [("caddy", "127.0.0.1", "18080", "8080")])

    def test_compose_network_is_internal(self):
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
