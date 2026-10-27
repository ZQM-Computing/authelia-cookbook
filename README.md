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

An **Authelia cookbook** for single sign-on and two-factor authentication patterns in front of self-hosted services. It currently contains one isolated access-control exercise. It is not a fleet-verified or production-certified deployment. Validate examples against the exact versions and environment you intend to use.

## Repository role and status

**Status:** Active, public — one isolated access-control example with CI configuration and runtime smoke tests.

**Audience:** Engineers exploring identity-aware access controls for self-hosted services.

**Portfolio:** Part of the ZQM Computing cookbook collection, indexed by [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks).

**Evidence boundary:** CI runs standard-library configuration contract tests, validates Compose syntax, validates the configuration with the pinned Authelia image, generates a throwaway Argon2 password hash in the ephemeral CI workspace, starts the service, and probes its health endpoint. This proves the sample configuration can start in that CI environment. It does not validate a browser login, reverse-proxy integration, forwarded-header trust, MFA, recovery, direct-origin bypass, or production readiness.

## Prerequisites

- Docker Engine and Docker Compose plugin
- Local-only test environment
- Optional local reverse proxy and hosts-file entries for manual browser testing

## Example

| Path | Purpose | Evidence level |
|---|---|---|
| [01-isolated-access-control](examples/01-isolated-access-control/) | Loopback-bound Compose service; deny-by-default policy with explicit demo rules and a synthetic identity placeholder | Contract tests, pinned-image config validation, service startup, and HTTP health probe in CI; no proxy/authentication integration test yet |

Run the example instructions from [its README](examples/01-isolated-access-control/README.md). The committed password hash is deliberately invalid. CI substitutes a newly generated throwaway hash only in its disposable workspace; it does not change the tracked file. For local authentication testing, generate and insert a local throwaway hash using the matching Authelia CLI. Never commit credentials or real secrets.

## Safety and operational limits

- Do not expose the example to a public network or use real accounts.
- A bypass rule is included only for a clearly named reserved demo domain; do not copy it blindly into a real deployment.
- Authentication policy does not prove reverse-proxy correctness. Verify trusted headers, direct-origin access, TLS, session cookies, MFA, recovery, and authorization end to end.
- Automated checks cover only configured paths and environments and do not constitute security certification.

## Roadmap

1. Add an isolated reverse-proxy integration test with explicit allow/deny cases, including the protected route, the intentionally bypassed demo route, and an unlisted host.
2. Test proxy header handling and confirm direct access to the protected upstream cannot bypass the proxy's authorization decision.
3. Add MFA and recovery guidance only after those flows have been exercised and the tested version/environment is recorded.

## Contributing

Keep examples synthetic and reproducible. Report security issues to <zqmcomputing@gmail.com>; do not disclose vulnerabilities in public issues.

## More from this series

- [caddy-cookbook](https://github.com/ZQM-Computing/caddy-cookbook) — HTTPS reverse proxy patterns
- [vaultwarden-cookbook](https://github.com/ZQM-Computing/vaultwarden-cookbook) — Self-hosted password vault and synthetic backup/restore drill
- [portainer-cookbook](https://github.com/ZQM-Computing/portainer-cookbook) — Container management
