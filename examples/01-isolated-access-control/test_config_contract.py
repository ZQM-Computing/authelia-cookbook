"""Small standard-library checks for the documented policy contract.

These checks are deliberately not a YAML parser or an Authelia integration test.
Run the actual image/config validation separately with Docker Compose.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).parent
CONFIG = (ROOT / "configuration.yml").read_text(encoding="utf-8")
USERS = (ROOT / "users_database.yml").read_text(encoding="utf-8")
COMPOSE = (ROOT / "compose.yaml").read_text(encoding="utf-8")


class AccessControlContractTests(unittest.TestCase):
    def test_default_is_deny(self):
        self.assertIn("default_policy: deny", CONFIG)

    def test_only_explicit_demo_domains_are_listed(self):
        self.assertIn('domain: "public.example.test"', CONFIG)
        self.assertIn('domain: "protected.example.test"', CONFIG)
        self.assertNotIn("domain: '*'", CONFIG)

    def test_protected_domain_requires_authentication(self):
        self.assertIn('domain: "protected.example.test"\n      policy: one_factor', CONFIG)

    def test_port_is_loopback_only(self):
        self.assertIn('"127.0.0.1:9091:9091"', COMPOSE)
        self.assertNotIn('"9091:9091"', COMPOSE)

    def test_image_uses_an_explicit_version_not_latest(self):
        self.assertIn("image: authelia/authelia:4.39.28", COMPOSE)
        self.assertNotIn(":latest", COMPOSE)

    def test_container_does_not_restart_automatically(self):
        self.assertIn('restart: "no"', COMPOSE)

    def test_external_cookie_urls_use_https(self):
        self.assertIn('authelia_url: "https://auth.example.test"', CONFIG)
        self.assertIn('default_redirection_url: "https://protected.example.test"', CONFIG)

    def test_required_demo_secrets_are_explicit_placeholders(self):
        self.assertIn('jwt_secret: "synthetic-demo-', CONFIG)
        self.assertIn('encryption_key: "synthetic-demo-', CONFIG)

    def test_credentials_are_obviously_synthetic_and_incomplete(self):
        self.assertIn("REPLACE_WITH_A_REAL_AUTHELIA_GENERATED_HASH", USERS)
        self.assertIn("example.test", USERS)
        self.assertIn('password: "$argon2id$REPLACE_WITH_A_REAL_AUTHELIA_GENERATED_HASH"', USERS)
        self.assertIn('email: "demo@example.test"', USERS)


if __name__ == "__main__":
    unittest.main()
