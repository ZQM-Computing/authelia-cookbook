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

A **Authelia cookbook** for single sign-on and two-factor authentication patterns in front of self-hosted services. This repository now contains an initial isolated access-control exercise; it is not a fleet-verified or production-certified deployment. Validate examples against the exact versions and environment you intend to use.

## Repository role and status

**Status:** Active, public — initial example submitted for review in [PR #2](https://github.com/ZQM-Computing/authelia-cookbook/pull/2).

**Audience:** Engineers exploring identity-aware access controls for self-hosted services.

**Portfolio:** Part of the ZQM Computing cookbook collection, indexed by [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks).

**Evidence boundary:** The included Python tests assert selected configuration text. CI now also invokes Authelia's own configuration validator against the pinned image, but this does not validate a live authentication flow, reverse-proxy integration, or production readiness. See the example README for the remaining runtime checks.

## Prerequisites

- Docker Engine and Docker Compose plugin
- Local-only test environment
- Optional local reverse proxy/hosts entries to exercise browser redirects

## Example

| Path | Purpose | Evidence level |
|---|---|---|
| [01-isolated-access-control](examples/01-isolated-access-control/) | Loopback-bound Compose service; deny-by-default policy with explicit demo rules; synthetic identity placeholder | Configuration contract tests included; runtime validation still required |

Run the example instructions from [its README](examples/01-isolated-access-control/README.md). The user password hash is deliberately invalid until replaced locally with a throwaway generated hash; never commit credentials.

## Safety and operational limits

- Do not expose the example to a public network or use real accounts.
- A bypass rule is included only for a clearly named reserved demo domain; do not copy it blindly into a real deployment.
- Authentication policy does not prove reverse-proxy correctness. Verify trusted headers, direct-origin access, TLS, session cookies, MFA, recovery, and authorization end to end.
- Automated checks cover only configured paths and environments and do not constitute security certification.

## Roadmap

1. Add an isolated reverse-proxy integration test with explicit allow/deny cases and test both protected and bypass routes.
2. Generate a throwaway local password hash in the test harness so authentication can be exercised without committing credentials.
3. Add MFA/recovery guidance and versioned evidence only after those paths are exercised.

## Contributing

Keep examples synthetic and reproducible. Report security issues to <zqmcomputing@gmail.com>; do not disclose vulnerabilities in public issues.

## More from this series

- [caddy-cookbook](https://github.com/ZQM-Computing/caddy-cookbook) — HTTPS reverse proxy patterns
- [vaultwarden-cookbook](https://github.com/ZQM-Computing/vaultwarden-cookbook) — Self-hosted password vault and synthetic backup/restore drill
- [portainer-cookbook](https://github.com/ZQM-Computing/portainer-cookbook) — Container management
