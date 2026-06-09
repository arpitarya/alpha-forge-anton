---
id: project-cdp-prerequisite
domain: project
type: memory
subtype: project
scope: shared
status: active
created: 2026-06-09
updated: 2026-06-09
related: [cdp-chrome, probe-cdp-not-playwright, project-broker-prime]
keywords: [cdp, chrome, 9299, prerequisite, sync, login, runbook]
---
Every API-kind broker sync (and every probe) depends on an **externally launched
Chrome** that the code does not start: run it with `--remote-debugging-port=9299
--user-data-dir=$HOME/.cache/alphaforge-anton-chrome` and **manually log in** to
each broker inside it. The backend only *attaches* over CDP ([[cdp-chrome]]) — it
never owns the browser lifecycle or the credentials.

**Why:** this is invisible from the code. Without that Chrome running and logged in,
`fetch()` hangs ~180s then errors and the source shows `ERROR`/`UNCONFIGURED` — a
confusing failure that looks like a bug but is missing setup. The same Chrome is
required for `probes/` verification ([[probe-cdp-not-playwright]]).

**How to apply:** before triggering a live sync or running a probe, confirm the
debugging Chrome is up and the broker tab is logged in. Credentials still come from
the [[afbach-vault]] (the user ID), and the startup prime
([[project-broker-prime]]) will auto-sync `READY` sources once both are in place.
