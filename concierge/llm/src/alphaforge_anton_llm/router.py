"""QueryRouter — maps QueryType to a ranked provider fallback chain."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import QueryType

logger = logging.getLogger(__name__)

# Default chains: first available provider wins; next takes over on error/rate-limit.
# Authored in the registry manifest (`registry/routing.json`), not here — see Fux
# rule `concierge-registry-single-source`. Eval overrides still layer on top below.

_EVAL_RESULTS = Path(__file__).parent.parent.parent / "eval" / "results" / "latest.json"


def _default_chains() -> dict[QueryType, list[str]]:
    return {QueryType(slug): chain for slug, chain in registry.chains().items()}


class QueryRouter:
    def __init__(self) -> None:
        self._chains = _default_chains()
        self._load_eval_overrides()

    def _load_eval_overrides(self) -> None:
        if not _EVAL_RESULTS.exists():
            return
        try:
            data = json.loads(_EVAL_RESULTS.read_text())
            for qt_slug, chain in data.get("chains", {}).items():
                try:
                    qt = QueryType(qt_slug)
                    self._chains[qt] = chain
                except ValueError:
                    pass
        except Exception as exc:
            logger.warning("Could not load eval overrides: %s", exc)

    def chain_for(self, query_type: QueryType) -> list[str]:
        return list(self._chains.get(query_type, ["gemini", "groq"]))

    def pick(
        self,
        query_type: QueryType,
        available: set[str],
    ) -> str | None:
        for provider in self.chain_for(query_type):
            if provider in available:
                return provider
        return None
