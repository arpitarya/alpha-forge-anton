---
defence: [HAL, BEL, BDL, MAZDOCK, COCHINSHIP, BEML, DATAPATTNS, SOLARINDS]
solar: [WAAREEENER, PREMIERENE, SUZLON, INOXWIND, BORORENEW]
capex_td: [SIEMENS, ABB, CGPOWER, BHEL, POWERINDIA, KEC]
ev_auto: [TATAMOTORS, M&M, OLAELEC, EXIDEIND, SONACOMS, UNOMINDA]
specialty_chem: [PIIND, AARTIIND, NAVINFLUOR, DEEPAKNTR, SRF, ATUL, VINATIORGA, FINEORG]
---

# Theme universe seed — constituent symbols per theme

NSE base tickers only (`quote_source.to_yahoo` appends `.NS`/`.BO`), **no personal
figures → git-safe**. `universe.py` reads this when `strategy.config universe.mode
= themes`, taking the union of the configured `universe.themes`.

This is a **starter set** — review and tune the constituents with Orff (Phase 3,
conversationally). Adding/removing a symbol here changes what `/signals/screen`
ranks, deterministically.
