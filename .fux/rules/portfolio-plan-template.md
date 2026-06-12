---
id: portfolio-plan-template
domain: portfolio
type: glossary
status: active
created: 2026-06-11
updated: 2026-06-12
---
# portfolio-plan-template

The shape every plan document follows: YAML `targets` (must sum to 100), `bands`
(drift tolerance in points), `rules`, `horizon`, plus prose goals. **Content lives
in the private elgar store** — linked, never stored, per [[plan-store]]:

> `elgar://plan/portfolio-plan-template` — read it with `elgar get portfolio-plan-template`

`plan_loader.py` parses the fenced YAML block of any doc following this template.

## Related

[[plan-store]] · [[core-allocation]] · [[secure-holdings-plan]]
