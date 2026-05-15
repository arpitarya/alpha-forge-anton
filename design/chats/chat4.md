# UI Layout Optimization

_Started 2026-05-15 16:38 UTC_

---

## User

make top bar and bottom bar(ai voice) more slim/sleek should be there on every page may be auto hide to provide more space. provide setting in preferences for the same

the cards for overall: total value invested unrealised p&l xirr, all wallets in a way so that it takes lessor space and main context that is tree  and ledger takes most of the space.

maybe make it collapsable or some better approach

## Assistant

_[tool: list_files]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: update_todos]_

I'll make the top bar and voice bar slimmer and globally available with auto-hide, plus collapse the portfolio summary cards into a compact strip. Let me lay out my plan:

_[tool: str_replace_edit]_

Let me make the edits. First the CSS, HTML structure and slim bars in the main file:

_[tool: str_replace_edit]_

_[tool: str_replace_edit]_

_[tool: str_replace_edit]_

Now add tweak defaults for chrome mode and apply them in tweaks-app.jsx:

_[tool: str_replace_edit]_

Now add the new preferences UI rows. Let me add them in the Display section, plus add a couple of tweak controls in the dev panel:

_[tool: str_replace_edit]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: str_replace_edit]_

_[tool: str_replace_edit]_

Let me also add the chrome controls to the dev Tweaks panel for parity:

_[tool: update_todos]_

_[tool: done]_

_[tool: fork_verifier_agent]_

Done. Summary:

- **Slim top bar** (4px vertical padding, smaller logo/nav) appears on every screen.
- **Voice bar moved to global** — now sits at the bottom of every page (Terminal, Portfolio, Preferences), much slimmer.
- **Auto-hide mode** collapses both bars to a thin accent strip; hover or focus reveals them.
- **Portfolio summary collapsed** into a single compact strip: inline TOTAL / INVESTED / P&L / XIRR + small wallet pills; a "More" toggle reveals the original full stat cards + wallet card strip. Tree/ledger now occupies the dominant vertical space.
- **Preferences → Display → Chrome** group: "Always visible / Auto-hide" segment + "Show voice bar" toggle (also mirrored in the dev Tweaks panel).

## User

Verifier agent check completed

## Assistant

All clean. Verifier confirms slim bars, compact portfolio summary with expand, and the new auto-hide preference all working as intended.

