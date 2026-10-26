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

A **Authelia cookbook** — single sign-on and two-factor authentication for proxied services. Queued in wave-11 (Node-3 hub set). Patterns are planned from the design, not yet from fleet runs. It is intended for Engineers who add SSO and 2FA in front of self-hosted services. Validate each pattern against your own data, software versions, and operating environment before adopting it.

## Repository role and status

**Status:** Active, public — seeding. Pattern passes land in follow-up work from fleet-verified setups; the tables below list what is planned, not what is already written.

**What this repository is:** Authelia patterns — see the table below.

**What it contributes:** Part of the ZQM Computing geospatial portfolio. The umbrella index for the series is [geospatial-cookbooks](https://github.com/ZQM-Computing/geospatial-cookbooks).

**Standing:** This repository is maintained independently. Automated checks cover only the paths and environments configured in its workflows; they do not establish production readiness or operational certification.

## Who this is for

Engineers who add SSO and 2FA in front of self-hosted services.

## Prerequisites

- Authelia via Docker
- Caddy as a reverse proxy (see caddy-cookbook)
- A user backend (file or LDAP)

## Patterns (planned)

| # | Example | What it will demonstrate |
|---|---------|--------------------------|
| 01 | `01-first-setup` | A first Authelia deployment with file users |
| 02 | `02-two-factor` | TOTP two-factor enrollment and recovery |
| 03 | `03-caddy-pairing` | Forward-auth integration with Caddy |
| 04 | `04-access-rules` | Access control rules per service and user group |

## Repository layout

```text
authelia-cookbook/
├── examples/          # pattern passes, landing in follow-up work
├── README.md
└── LICENSE
```

## Roadmap

- First pattern pass: the first two table rows
- Second pass: the remaining rows, from fleet-verified setups

## Contributing

A contributing guide lands with the first pattern pass. Report security issues to <zqmcomputing@gmail.com> — please do not open a public issue for those.

## More from this series

- [caddy-cookbook](https://github.com/ZQM-Computing/caddy-cookbook) — Automatic-HTTPS reverse proxying from config and API
- [vaultwarden-cookbook](https://github.com/ZQM-Computing/vaultwarden-cookbook) — Self-hosted password vault with clients and API
- [portainer-cookbook](https://github.com/ZQM-Computing/portainer-cookbook) — Container management with an API and UI
