# Postmortem: Caddy crash loop caused by unavailable directive

**Status:** resolved  
**Severity:** development deployment blocked  
**Customer impact:** the HTTPS entry point could not start during the affected deployment; this occurred while establishing the platform, before a production availability commitment existed.

## Summary

Caddy repeatedly exited during startup because the configuration referenced the `rate_limit` directive. The deployed `caddy:2-alpine` image does not contain the third-party rate-limit module required to register that directive.

## Detection

Container status showed Caddy restarting instead of remaining healthy. `docker logs caddy` reported that `rate_limit` was not a registered directive.

## Timeline

Exact historical timestamps were not retained. Relative sequence:

1. A configuration containing `rate_limit` was deployed with the stock Caddy image.
2. Caddy rejected the configuration and entered a restart loop.
3. Container logs identified the unregistered directive.
4. The plugin-dependent block was disabled.
5. Caddy started successfully and HTTPS routing was reverified.

The missing timestamps are themselves a process gap; future drills and incidents record UTC detection, acknowledgement, mitigation, and recovery times.

## Root cause

The configuration and runtime artifact had incompatible assumptions. The configuration required a third-party Caddy module, while Compose selected the stock image, which contains only standard modules.

## Contributing factors

- Configuration validity was not checked against the exact runtime image before deployment.
- The optional plugin dependency was not visible at the image-selection boundary.
- Startup failure was detected after deployment rather than in CI.

## What went well

- The process failed closed instead of starting with an unknown configuration.
- Container logs exposed a precise error message.
- The change was reversible and did not require infrastructure replacement.

## Corrective actions

| Action | Status | Verification |
|---|---|---|
| Keep plugin-only directives disabled while using the stock image | Complete | Current Caddyfile parses without `rate_limit` enabled |
| Document the custom-image requirement next to the optional configuration | Complete | Guidance is present in `caddy/Caddyfile` |
| Treat runtime configuration as versioned deployment input | Complete | CD copies the checked-in Caddyfile before deployment |
| Add an image-specific Caddy configuration validation step | Complete | CI runs `caddy validate` using `caddy:2-alpine` |

## Lesson

Configuration correctness depends on the runtime artifact, not only on syntax. Validation must use the same image and modules that will run on the host.
