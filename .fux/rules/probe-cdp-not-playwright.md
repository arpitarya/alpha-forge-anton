---
id: probe-cdp-not-playwright
domain: brokers
type: convention
status: active
created: 2026-06-09
updated: 2026-06-17
keywords:
  - probe
  - cdp
  - chrome
  - 9299
  - playwright
  - mcp
  - verification
  - xhr
code_refs:
  - probes/Probes.md
  - probes/WHY_PROBES_NOT_MCP.md
  - backend/app/modules/brokers/_cdp.py
related:
  - broker-source-contract
  - broker-source-integration
---
**Convention:** UI and broker verification is done with scripts in `probes/` that
attach to the already-running AlphaForge Anton Chrome over CDP on port **9299**
(`BROKER_CDP_PORT`, see [_cdp.py](../../backend/app/modules/brokers/_cdp.py)) —
**never** the Playwright MCP server. A new feature or broker isn't "verified" until
it has a probe in `probes/` and a `just` recipe to run it.

**Why:** the brokers are authenticated in *your* real Chrome session (manual login,
2FA), and the backend reads the live XHR / `enctoken` off that same session. A
Playwright MCP browser is a fresh, unauthenticated context — it cannot see your
holdings, would force re-login, and verifies nothing about the path the backend
actually takes. Probes exercise the real CDP attach the production code uses, so a
green probe means the real fetch works. Full rationale:
[WHY_PROBES_NOT_MCP.md](../../probes/WHY_PROBES_NOT_MCP.md).

**How to apply:** start Chrome with `--remote-debugging-port=9299
--user-data-dir=$HOME/.cache/alphaforge-anton-chrome` and log in to the broker
there. Write `probes/{slug}_probe.py` (XHR interception or `enctoken` → direct REST)
and wire a `just` recipe. To discover an endpoint shape, run the probe *before*
implementing the source's `normalize()`. How to author one: [Probes.md](../../probes/Probes.md).
