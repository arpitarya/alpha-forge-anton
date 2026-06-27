"""Funding plane — the fixed-cost side of the self-funding ledger.

`subscriptions.toml` is a deterministic ($0) registry of flat opex (Claude, Parallel,
ElevenLabs, …); `funding_subscriptions.opex_per_month()` is the INR figure that populates
`contracts.Objective.self_funding.opex_per_month`. No secrets live here — only public
provider names and list prices. See docs/cage.md for how this baseline relates to Cage.

`covered` resolves once a realised-P&L source exists (Gate-4 paper); cage savings reduce
opex, they are not income — `self_funding()` keeps `covered` honest-pending (None).
"""
