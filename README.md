# Authelia Cookbook

<!-- ZQM-START -->
<!-- markdownlint-disable MD033 -->
<p align="center">
  <strong>ZQM Computing — Geospatial Engineering & Scientific Computing</strong><br>
  <a href="https://github.com/ZQM-Computing">ZQM Computing</a>
</p>
<!-- markdownlint-enable MD033 -->
<!-- ZQM-END -->

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

An **Authelia cookbook** for single sign-on and two-factor authentication patterns in front of self-hosted services. It contains an isolated Authelia configuration exercise and a disposable Caddy forward-auth integration fixture. It is not a fleet-verified or production-certified deployment. Validate examples against the exact versions and environment you intend to use.

## Repository role and status

**Status:** Active, public — one configuration/startup exercise and one reverse-proxy integration fixture with positive and negative authentication assertions.

**Audience:** Engineers exploring identity-aware access controls for self-hosted services.

**Portfolio:** Part of the ZQM Computing cookbook collection, indexed by [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks).

**Evidence boundary:** CI validates the Authelia configuration, Compose syntax, pinned-image configuration, service startup and health endpoint. The proxy fixture checks public routing, denial without a session, a valid synthetic first-factor session, protected-upstream access, identity-header propagation against the expected demo identity, unauthenticated identity-header spoofing, unknown-host handling, and loopback-only published ports. Static regression guards require `forward_auth` and prevent published ports on the protected upstream and Authelia. This remains a pinned local fixture, not proof of production readiness or separately deployed direct-origin protection.

## Prerequisites

- Docker Engine and Docker Compose plugin
- Python 3.11 or newer for the standard-library smoke tests
- Local-only test environment
- No real accounts, credentials, production domains, or production services

## Examples

| Path | Purpose | Evidence level |
|---|---|---|
| [01-isolated-access-control](examples/01-isolated-access-control/) | Loopback-bound Authelia service with deny-by-default policy and synthetic identity placeholder | Contract tests, pinned-image config validation, service startup, and HTTP health probe |
| [02-proxy-integration](examples/02-proxy-integration/) | Disposable Caddy + Authelia + public/protected synthetic upstreams | Runtime checks for public routing, unauthenticated denial, authenticated access and identity headers, spoofing, unknown hosts, and port exposure; static configuration regression guards |

Run the existing configuration exercise from [its README](examples/01-isolated-access-control/README.md). The committed password hash is deliberately invalid. CI substitutes a newly generated throwaway hash only in its disposable workspace; it does not change the tracked file. Never commit credentials or real secrets.

The proxy fixture can be started from its directory with:

```sh
docker compose config --quiet
docker compose up -d --no-build
python -m unittest -v test_proxy_smoke.py
docker compose down --volumes --remove-orphans
```

The fixture publishes Caddy's HTTP test listener on `127.0.0.1:18080` and HTTPS test listener on `127.0.0.1:18443`. Authelia and both upstreams have no published host ports and remain on a dedicated internal Compose network; Caddy joins a separate host-access bridge. Protected-route checks use HTTPS, as required for Authelia session-cookie authorization. Always run it in an isolated local environment. CI generates a throwaway password at runtime and passes it to the test process through the job environment; never commit the generated password or hash. The positive-path test logs in through Authelia's first-factor API and asserts the protected upstream receives the expected synthetic identity headers.

## Safety and operational limits

- Do not expose either example to a public network or use real accounts.
- The bypass policy applies only to the explicitly named reserved demo domain; do not copy it blindly into a real deployment.
- Authentication policy does not prove reverse-proxy correctness. Verify trusted headers, direct-origin access, TLS, session cookies, MFA, recovery, and authorization end to end.
- Automated checks cover only configured paths and environments and do not constitute security certification.

## Roadmap

1. Complete the positive authenticated-session test and verify the expected identity headers at the protected upstream.
2. Add deliberate regression checks proving removal of `forward_auth` and publication of the protected upstream cause CI failure.
3. Test direct-origin protections for a separately deployed environment before making any deployment-specific claim.
4. Add MFA and recovery guidance only after those flows have been exercised and the tested version/environment is recorded.

## Contributing

Keep examples synthetic and reproducible. Report security issues to <zqmcomputing@gmail.com>; do not disclose vulnerabilities in public issues.

## More from this series

- [caddy-cookbook](https://github.com/ZQM-Computing/caddy-cookbook) — HTTPS reverse proxy patterns
- [vaultwarden-cookbook](https://github.com/ZQM-Computing/vaultwarden-cookbook) — Self-hosted password vault and synthetic backup/restore drill
- [portainer-cookbook](https://github.com/ZQM-Computing/portainer-cookbook) — Container management
