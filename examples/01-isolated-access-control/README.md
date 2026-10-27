# Isolated Authelia access-control example

This is a local configuration exercise, not a production deployment. It binds
the Authelia port to loopback and uses reserved `.test` names. The example
intentionally denies every domain except the explicitly listed policies.

## Prerequisites

- Docker Engine and the Docker Compose plugin
- A local hosts-file or reverse-proxy setup only if testing browser redirects
- No real accounts, credentials, or production services

## Validate and start

From this directory:

```sh
docker compose config
```

Review the rendered configuration before starting. The user password is an
intentionally invalid placeholder, so successful authentication is not expected
until a throwaway test hash is generated using the matching Authelia CLI and
inserted locally. Do not commit that local replacement.

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
- A typo or unsupported policy: configuration validation/startup should fail;
  verify this against the exact image version before relying on it operationally.

The domain rules demonstrate Authelia policy configuration only. They do not
prove that a reverse proxy forwards identity headers safely or that a deployed
service is protected. For a real integration, test proxy routing, header
stripping, TLS, cookie scope, MFA, account recovery, and direct-origin access.

## Safety boundary

Loopback binding limits host exposure but is not a substitute for host security.
Use synthetic identities, do not add real secrets to Git, and do not expose this
configuration to a public network. This example is not production-ready.
