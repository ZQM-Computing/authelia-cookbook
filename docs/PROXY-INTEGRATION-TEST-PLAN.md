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
3. The protected route without a valid session does not return the protected marker and produces the expected authentication redirect or denial response.
4. A valid session established through a supported Authelia flow reaches the protected route and returns the protected marker. This positive assertion is mandatory; a test suite that blocks every request must fail.
5. A request to an unknown `.test` host returns the fixture's explicitly configured no-route status (prefer a deterministic `404`) and neither synthetic upstream marker appears in the response. Do not accept merely “not the expected marker” as sufficient.
6. Client-supplied `Remote-User`, `Remote-Groups`, `Remote-Name`, and `Remote-Email` values cannot authenticate a request or appear as trusted identity at the protected upstream. Verify both unauthenticated spoofing and the identity values delivered after a successful authentication flow.
7. The protected upstream and Authelia have no published host ports; the sole published test port is explicitly loopback-bound. Assert the rendered Compose port mappings, not only a hand-maintained expectation.
8. A deliberate regression removing `forward_auth` makes the protected-route authorization test fail.
9. A deliberate regression publishing the protected upstream port makes the exposure assertion fail.
10. The test reports useful service logs on failure and always cleans up containers and volumes, including when a request or assertion fails.

## Important boundary

If the CI fixture cannot establish a valid session through a supported Authelia flow without brittle internals, record that limitation and keep the claim narrow; do not weaken or silently skip the positive assertion. Any skipped test must be surfaced as skipped and must not be described as full authorization coverage.

This fixture will demonstrate behavior only for the pinned images and test topology. It will not establish TLS termination, external DNS correctness, firewall policy, direct-origin protection in a separately deployed environment, MFA policy adequacy, or production readiness. The absence of published upstream ports demonstrates isolation in this Compose fixture; it does not prove a separately deployed origin is unreachable.

## Implementation exit criteria

- The fixture and assertions run from a clean checkout using the repository's documented command.
- CI executes the integration test on relevant pull requests and main-branch changes.
- Positive authenticated access, unauthenticated denial, spoofed-header rejection, and deterministic unknown-host behavior are all mandatory assertions.
- Regression checks demonstrate that removing `forward_auth` or publishing the protected upstream port causes CI to fail.
- README claims distinguish config/startup validation from end-to-end authorization evidence.
- The pull request contains recorded CI evidence; no deployment or production configuration changes are part of this work.

## References

- [Authelia Caddy integration](https://www.authelia.com/integration/proxies/caddy/)
- [Authelia forward-auth authorization endpoint](https://www.authelia.com/configuration/miscellaneous/server-endpoints-authz/)
- [Caddy `forward_auth` directive](https://caddyserver.com/docs/caddyfile/directives/forward_auth)
