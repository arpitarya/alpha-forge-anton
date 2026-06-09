---
id: cdp-chrome
domain: brokers
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/_cdp.py
related: [probe-cdp-not-playwright, enctoken, broker-source-integration]
aliases: [CDP, remote debugging, 9299, debugging chrome]
keywords: [cdp, chrome, 9299, remote-debugging, attach, xhr]
---
**Term:** CDP Chrome (port 9299)

**Definition:** The user's own Chrome, started with
`--remote-debugging-port=9299 --user-data-dir=$HOME/.cache/alphaforge-anton-chrome`,
where the user manually logs in to each broker (password + 2FA stay local). The
backend **attaches** to this running browser over the Chrome DevTools Protocol
(`_cdp.py`, port from `BROKER_CDP_PORT`, default 9299) to read the authenticated
`enctoken` cookie ([[enctoken]]) or execute an in-page `fetch()`. Anton never sees
credentials — it reads live XHR off an already-authenticated session. This is also
why verification uses CDP probes, not a fresh Playwright browser
([[probe-cdp-not-playwright]]).
