"""CostGuard — blocks paid providers unless explicitly confirmed."""

from __future__ import annotations


class CostGuardError(Exception):
    """Raised when a paid provider is invoked without user confirmation."""

    def __init__(self, provider: str, est_tokens: int = 0) -> None:
        self.provider = provider
        self.est_tokens = est_tokens
        super().__init__(
            f"Provider '{provider}' is paid. Set confirmed=True in EscalationRequest to proceed."
        )


class CostGuard:
    """Singleton guard; tracks which providers incur real cost."""

    _PAID_PROVIDERS: frozenset[str] = frozenset({"claude-sdk"})

    def check(self, provider: str, *, confirmed: bool = False) -> None:
        if provider in self._PAID_PROVIDERS and not confirmed:
            raise CostGuardError(provider)
