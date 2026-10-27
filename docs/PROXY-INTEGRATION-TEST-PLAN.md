# Reverse-proxy authorization integration test plan

## Status and scope

**Status: partial smoke fixture added; full authorization coverage is not implemented or runtime-verified.** The disposable fixture in [examples/02-proxy-integration](../examples/02-proxy-integration/) now defines Caddy, Authelia, and two synthetic upstreams. Its intended smoke checks cover public routing, denial without a session, unauthenticated identity-header spoofing, deterministic unknown-host handling, and loopback-only port publication. CI evidence for this fixture is still pending.

The current smoke tests do **not** establish a valid authenticated session or verify identity headers after successful authentication. Do not describe this as complete end-to-end authorization coverage until those positive-path tests are implemented and pass.

## Fixture safety boundaries

- Pin Caddy, Authelia, and test-upstream images to explicit versions; avoid floating `latest` tags.
- Put all services on a dedicated internal Compose network.
- Publish only the Caddy test listener, bound to `127.0.0.1`; do not publish Authelia or either upstream.
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

These are smoke tests, not proof that an authenticated user can reach the protected upstream.

## Remaining mandatory authorization work

1. Establish a valid session through a supported Authelia login flow using only the synthetic demo account.
2. Prove the valid session reaches the protected upstream and returns its marker.
3. Verify identity headers delivered after successful authentication are the expected synthetic identity, not client-supplied spoofed values.
4. Demonstrate that removing Caddy `forward_auth` makes the protected-route test fail.
5. Demonstrate that publishing the protected upstream port makes the exposure assertion fail.
6. Ensure a missing or skipped positive-path test cannot be reported as full authorization coverage.

If the CI fixture cannot establish a valid session without brittle internals, document the limitation and keep claims narrow; do not weaken or silently skip the positive assertion.

## Evidence boundary

The fixture demonstrates behavior only for its pinned images and test topology. It does not establish TLS termination, external DNS correctness, firewall policy, direct-origin protection in a separately deployed environment, MFA policy adequacy, recovery behavior, or production readiness. The absence of published upstream ports demonstrates isolation in this Compose fixture; it does not prove a separately deployed origin is unreachable.

## References

- [Authelia Caddy integration](https://www.authelia.com/integration/proxies/caddy/)
- [Authelia forward-auth authorization endpoint](https://www.authelia.com/configuration/miscellaneous/server-endpoints-authz/)
- [Caddy `forward_auth` directive](https://caddyserver.com/docs/caddyfile/directives/forward_auth)
