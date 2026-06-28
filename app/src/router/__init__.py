"""FaberLoom SL1a provider router."""

from .engine import BudgetExceeded, Router
from .models import CompletionRequest, CompletionResult, ProviderConfig, RouterSettings, UsageRecord
from .providers import Provider, ProviderError
from .registry import build_router

__all__ = [
    "Router",
    "Provider",
    "CompletionRequest",
    "CompletionResult",
    "ProviderConfig",
    "RouterSettings",
    "UsageRecord",
    "ProviderError",
    "BudgetExceeded",
    "build_router",
]
