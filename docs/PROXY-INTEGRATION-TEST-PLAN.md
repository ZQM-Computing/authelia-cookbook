# Reverse-proxy authorization integration test plan

## Status and scope

**Status: positive-session test implemented; latest full CI run has not passed yet, so authenticated authorization is not yet runtime-verified.** The disposable fixture in [examples/02-proxy-integration](../examples/02-proxy-integration/) now defines Caddy, Authelia, and two synthetic upstreams. Its intended smoke checks cover public routing, denial without a session, unauthenticated identity-header spoofing, deterministic unknown-host handling, and loopback-only port publication. CI smoke evidence: [workflow run 40443070947](https://github.com/ZQM-Computing/authelia-cookbook/actions/runs/40443070947) passed on commit `37a273bb36c419c739032037f5e413639f6c8c7e`. This validates the runtime smoke assertions listed below. Static regression guards now require the protected route's `forward_auth` directive and reject published Authelia/protected-upstream ports; those guards still need a passing CI run and are not a substitute for the positive-session path.

The test suite performs a synthetic first-factor login and checks protected-upstream access plus the expected identity headers. These positive-session and identity-header assertions passed in [workflow run 40445035046](https://github.com/ZQM-Computing/authelia-cookbook/actions/runs/40445035046) on commit `54699ddd0eedeac262ce4e1bb375b936141130a9`. The current head adds explicit mutation tests for both regression guards and still requires a fresh complete CI pass.

## Fixture safety boundaries

- Pin Caddy, Authelia, and test-upstream images to explicit versions; avoid floating `latest` tags.
- Keep Authelia and both upstreams on a dedicated internal Compose network. Caddy also joins a separate host-access bridge so its loopback-published test listeners remain reachable from the runner.
- Publish only Caddy test listeners, both bound to `127.0.0.1`; do not publish Authelia or either upstream. Use HTTPS for protected/auth-portal requests because Authelia requires secure schemes for session-cookie authorization.
- Use reserved `.test` hostnames and synthetic marker responses. No production domains, identities, credentials, or secrets.
- Configure Caddy `forward_auth` against Authelia's documented forward-auth endpoint and copy only the identity headers required by the test.
- Keep the fixture isolated from production services and never broaden trusted proxy ranges to make a test pass.
- Reuse only synthetic example credentials; generate the throwaway password hash in the CI workspace. Never commit generated credentials.
- Always tear down containers and volumes, including after failed assertions.

## Current smoke assertions

1. Compose renders successfully and the pinned Caddy and Authelia configurations validate.
2. The public synthetic route returns its expected marker without an authentication challenge.
3. The protected route without a session does not return the protected marker and returns an authentication denial/redirect response.
4. Client-supplied `Remote-User`, `Remote-Groups`, `Remote-Name`, and `Remote-Email` values cannot bypass the protected route without a valid session.
5. An unknown host returns the explicitly configured `404` and neither upstream marker appears.
6. The protected upstream and Authelia have no published host ports; only Caddy is published, explicitly bound to loopback.
7. CI collects fixture logs on failure and tears down both the fixture and the original isolated service.

The positive-path assertion proves authenticated access only for this pinned fixture. It deliberately supplies client-forged identity headers alongside the valid session and verifies the upstream receives the authenticated demo identity, not the forged values.

## Remaining mandatory authorization work

1. Obtain a clean CI pass for the valid-session and identity-header assertions.
2. Demonstrate the regression checks fail under deliberate `forward_auth` removal and protected-upstream port publication; the current guards are static configuration assertions, not mutation-run demonstrations.
3. Keep the positive-session assertion required and ensure it cannot be skipped while reporting full authorization coverage.

If the CI fixture cannot establish a valid session without brittle internals, document the limitation and keep claims narrow; do not weaken or silently skip the positive assertion.

## Evidence boundary

The fixture demonstrates behavior only for its pinned images and test topology. It does not establish TLS termination, external DNS correctness, firewall policy, direct-origin protection in a separately deployed environment, MFA policy adequacy, recovery behavior, or production readiness. The absence of published upstream ports demonstrates isolation in this Compose fixture; it does not prove a separately deployed origin is unreachable.

## References

- [Authelia Caddy integration](https://www.authelia.com/integration/proxies/caddy/)
- [Authelia forward-auth authorization endpoint](https://www.authelia.com/configuration/miscellaneous/server-endpoints-authz/)
- [Caddy `forward_auth` directive](https://caddyserver.com/docs/caddyfile/directives/forward_auth)
