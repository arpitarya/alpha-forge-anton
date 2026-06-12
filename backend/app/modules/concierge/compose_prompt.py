"""Build the system prompt that constrains Orff to the Fux component vocabulary."""

from __future__ import annotations

_RULES = (
    "You compose a UI for AlphaForge Anton by emitting ONLY a JSON UISpec — never code.\n"
    'A node is {"component": <name>, "props": {...}, "data": <hook?>, "children": [...]}\n'
    'or a text leaf {"text": "..."}. Use ONLY the components, props, and data hooks listed '
    "below — anything else is rejected by the validator. Prefer literal props (numbers and "
    'strings you already know). Naming a hook in "data" spreads its live fields into the '
    "node's props at render time — use it only when live values are needed. Respond with "
    "the JSON object only, no prose.\n\n"
)


def _sig(c: dict) -> str:
    props = ", ".join(p["name"] + ("?" if p["optional"] else "") for p in c["props"])
    return f"- {c['name']}({props})"


def _vocab(reg: dict) -> str:
    comps = "\n".join(_sig(c) for c in reg["components"])
    hooks = ", ".join(h["name"] for h in reg["hooks"]) or "(none)"
    return f"COMPONENTS (name(props)):\n{comps}\n\nDATA HOOKS: {hooks}"


def build_system(reg: dict) -> str:
    return _RULES + _vocab(reg)
