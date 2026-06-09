---
id: enctoken
domain: brokers
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - backend/app/modules/brokers/_http.py
related: [cdp-chrome, broker-source-integration]
aliases: [enc token, kite token, session token]
keywords: [enctoken, zerodha, kite, cookie, auth, session]
---
**Term:** enctoken

**Definition:** Zerodha Kite's session cookie. After manual login in the
[[cdp-chrome]], the helper reads the `enctoken` cookie over CDP and uses it to make
direct authenticated REST calls to the Kite OMS API
(`/oms/portfolio/holdings`, `/oms/user/margins`, `/api/mf/holdings`) with header
`X-Kite-Version: 3`. It is cached via `_http.save_session()` under
`~/.alphaforge-anton/sessions/{slug}.json` (`chmod 600`) and re-used until a 401/403
forces a fresh CDP read. Both the `zerodha` and `zerodha_coin` sources share one
enctoken.
