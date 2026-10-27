# Reverse-proxy authorization integration test plan

## Status and scope

**Status: planned; not implemented or runtime-verified.** The current isolated access-control example validates Authelia configuration, Compose syntax, container startup, and the health endpoint. Its contract tests do not exercise a reverse proxy or prove that a protected upstream is unreachable without authorization. Do not treat the existing checks as evidence of end-to-end access control.

This plan defines the minimum safe next step: a disposable Caddy + Authelia + two synthetic upstreams fixture that runs in CI and never connects to a production service.

## Required topology

- Pin the Caddy, Authelia, and test-upstream images to explicit versions; avoid floating `latest` tags.
- Put all services on a dedicated Compose network.
- Publish only the Caddy test listener, bound to `127.0.0.1`; do not publish Authelia or either upstream.
- Use reserved `.test` hostnames and synthetic marker responses. No production domains, identities, credentials, or secrets.
- Configure Caddy `forward_auth` against Authelia's documented forward-auth endpoint and copy only the identity headers required by the test.
- Configure Authelia to trust only the proxy/network hop required by this isolated fixture. Do not broaden trusted proxy ranges to make the test pass.
- Generate ephemeral session/signing values and a throwaway user password hash in the CI workspace. Never commit generated values.
- Always tear down containers and volumes, including after failed assertions.

## Required assertions

1. Compose renders successfully and both Authelia and Caddy configurations validate using their pinned images.
2. The public synthetic route returns its expected marker without an authentication challenge.
3. The protected route without a session does not return the protected marker and instead returns the documented authentication redirect or denial response.
4. A malformed or unknown host does not route to either synthetic upstream.
5. Identity headers supplied by the client are not trusted as authenticated identity; only headers set by the successful proxy-auth flow may reach the protected upstream.
6. The protected upstream and Authelia have no published host ports; the sole published test port is explicitly loopback-bound.
7. The test reports useful service logs on failure and always cleans up.

## Important boundary

An unauthenticated-request test alone is insufficient. Before claiming full authorization coverage, add a positive authenticated-session test and a negative test proving a client cannot spoof `Remote-User`/related identity headers. If the CI fixture cannot establish a valid session through a supported Authelia flow without brittle internals, record that limitation and keep the claim narrow rather than weakening the assertion.

This fixture will demonstrate behavior only for the pinned images and test topology. It will not establish TLS termination, external DNS correctness, firewall policy, direct-origin protection in a separately deployed environment, MFA policy adequacy, or production readiness.

## Implementation exit criteria

- The fixture and assertions run from a clean checkout using the repository's documented command.
- CI executes the integration test on relevant pull requests and main-branch changes.
- A deliberate regression that removes `forward_auth` causes the protected-route test to fail.
- A deliberate regression that publishes the protected upstream port causes the exposure assertion to fail.
- README claims distinguish config/startup validation from end-to-end authorization evidence.
- The pull request contains recorded CI evidence; no deployment or production configuration changes are part of this work.

## References

- [Authelia Caddy integration](https://www.authelia.com/integration/proxies/caddy/)
- [Authelia forward-auth authorization endpoint](https://www.authelia.com/configuration/miscellaneous/server-endpoints-authz/)
- [Caddy `forward_auth` directive](https://caddyserver.com/docs/caddyfile/directives/forward_auth)
