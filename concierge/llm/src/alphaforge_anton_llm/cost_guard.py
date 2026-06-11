"""CostGuard — blocks paid models unless explicitly confirmed.

Paid status is read per-model from the registry manifest (`consumption.paid` in
`providers.json`, via `pricing.is_paid`) — never a hardcoded provider list. Add a
paid model or reprice one by editing the JSON. See Fux rule
`concierge-registry-single-source`.
"""

from __future__ import annotations

from alphaforge_anton_llm import pricing


class CostGuardError(Exception):
    """Raised when a paid model is invoked without user confirmation."""

    def __init__(self, provider: str, est_tokens: int = 0) -> None:
        self.provider = provider
        self.est_tokens = est_tokens
        super().__init__(
            f"Provider '{provider}' is paid. Set confirmed=True in EscalationRequest to proceed."
        )


class CostGuard:
    """Singleton guard; gates any model whose registry `consumption.paid` is true."""

    def check(self, provider: str, *, model: str | None = None, confirmed: bool = False) -> None:
        if pricing.is_paid(provider, model) and not confirmed:
            raise CostGuardError(provider)
