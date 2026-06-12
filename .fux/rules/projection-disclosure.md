---
id: projection-disclosure
domain: concierge
type: convention
status: active
created: 2026-06-12
updated: 2026-06-12
code_refs:
  - backend/app/modules/plans/projection_service.py
  - backend/app/modules/concierge/holdings_private.py
related: [capital-market-assumptions, ui-component-contract, secure-holdings-plan]
aliases: [projection-honesty, no-guarantees, assumptions-cited]
keywords: [projection, disclosure, assumptions, real, nominal, guarantee]
---
**Convention:** every forward projection Orff presents must satisfy four
honesty requirements:

1. **Cited assumptions** — the response carries `assumptions_ref` pointing at
   [[capital-market-assumptions]]; the rate used is named, never implicit.
2. **Real beside nominal** — `projection_service.project` returns both series;
   showing only nominal flatters every long horizon and is treated as a bug.
3. **Estimates, not promises** — projected values are scenario outputs of an
   assumed constant rate. Language like "you will have" is wrong; "at X% pa
   this grows to" is right. Markets do not compound smoothly — actual paths
   include drawdowns ([[drawdown-recovery]]).
4. **No fabricated inputs** — projections run on user-supplied or live-plan
   figures. With no live data, Orff says so plainly and never renders a
   sample/demo table (enforced by the `holdings_private` no-data context).

**Why:** a projection in a finance terminal reads as authority. Uncited rates,
nominal-only charts, and certainty language are how honest math becomes
misleading advice — and once a fabricated demo table has scrolled past, the
user can no longer tell generated fiction from broker data (the 2026-06-12
"Demo Mode" incident).

**How to apply:** UI specs that chart projections (LineChart with `bandLo`/
`bandHi` via [[ui-component-contract]]) should plot the real series or both,
and label the assumed rate in the title or caption.
