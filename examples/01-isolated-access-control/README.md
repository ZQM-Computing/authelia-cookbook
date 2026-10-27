# Isolated Authelia access-control example

This is a local configuration exercise, not a production deployment. It binds
the Authelia port to loopback and uses reserved `.test` names. The example
intentionally denies every domain except the explicitly listed policies.

## Prerequisites

- Docker Engine and the Docker Compose plugin
- A local HTTPS reverse proxy and hosts-file setup if testing browser redirects
- No real accounts, credentials, or production services

## Validate and start

From this directory:

```sh
docker compose config
docker run --rm --volume "$PWD:/config:ro" authelia/authelia:4.39.28 authelia config validate --config /config/configuration.yml
```

Review the rendered configuration before starting. The committed user password
hash is an intentionally invalid placeholder. CI generates a throwaway
password, asks the pinned Authelia CLI to hash it, and substitutes the result
only in the disposable CI workspace before starting the service. For local
authentication testing, perform the same operation locally and replace the
placeholder in your working copy; do not commit the resulting hash or password.

The session, reset-password JWT, and storage encryption values are also
synthetic placeholders. Replace them locally for a real integration exercise
and never commit production secrets.

```sh
docker compose up --no-build
docker compose logs --follow authelia
```

Stop and remove the container with `docker compose down`. The local SQLite
database and notification file are stored in the container filesystem and are
not a backup strategy.

## Expected authorization behavior

- An unlisted domain: denied by `default_policy: deny`.
- `public.example.test`: bypasses authentication only because it is explicitly
  listed as a public demonstration route.
- `protected.example.test`: requires one-factor authentication.
- A typo or unsupported policy: configuration validation or startup should
  fail; verify this against the pinned image before relying on it operationally.

## What CI verifies

The workflow runs the standard-library configuration contract tests, validates
Compose syntax, validates the configuration with Authelia `4.39.28`, generates
an ephemeral valid Argon2 password hash, starts the service, and probes the
HTTP health endpoint. The generated hash exists only in the disposable CI
workspace; the tracked placeholder remains unchanged.

These checks demonstrate configuration validity and service startup in the CI
environment. They do **not** prove a browser login, reverse-proxy routing,
forwarded-header trust, TLS behavior, cookie scope, MFA, account recovery, or
that a protected upstream cannot be reached directly. Those require separate
integration tests and environment-specific evidence.

## Safety boundary

Loopback binding limits host exposure but is not a substitute for host security.
Use synthetic identities, do not add real secrets to Git, and do not expose this
configuration to a public network. This example is not production-ready.
