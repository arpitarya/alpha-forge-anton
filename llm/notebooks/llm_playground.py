# ---
# jupyter:
#   jupytext:
#     formats: py:light,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
# ---

# # LLM Gateway — Dev Playground
#
# Validate each provider standalone before wiring into the backend.

# %% [markdown]
# ## Setup

# %%
import asyncio, os, sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path.cwd().parents[1]
LLM_SRC = ROOT / "llm" / "src"
if str(LLM_SRC) not in sys.path:
    sys.path.insert(0, str(LLM_SRC))

# Load credentials (.env.cred.local takes highest priority)
for _f in [".env", ".env.local", ".env.cred.local"]:
    _p = ROOT / _f
    if _p.exists():
        load_dotenv(_p, override=True)

from alphaforge_llm import (
    REGISTRY, Message, QueryType, create_gateway, CostGuardError,
)
from alphaforge_llm.router import QueryRouter

def msg(role: str, content: str) -> Message:
    return Message(role=role, content=content)

QUERY = [msg("user", "What is the current trend for Nifty 50?")]
print("alphaforge_llm loaded OK")
print(f"Providers registered: {list(REGISTRY)}")

# %% [markdown]
# ## 1. Health check — all providers

# %%
gw = create_gateway()
healths = await gw.health()
print(f"{'Provider':<14} {'Available':<12} {'Error'}")
print("-" * 55)
for name, h in healths.items():
    avail = "✓" if h.available else "✗"
    err = (h.last_error or "")[:40]
    print(f"  {name:<12} {avail:<12} {err}")

# %% [markdown]
# ## 2. Groq — direct call

# %%
from alphaforge_llm.providers.groq import GroqAdapter

groq = GroqAdapter()
h = await groq.health()
print("Groq health:", h)
if h.available:
    r = await groq.complete(QUERY)
    print(f"Model: {r.model}  tokens: {r.prompt_tokens}+{r.completion_tokens}")
    print(r.content[:300])

# %% [markdown]
# ## 3. Cerebras — direct call

# %%
from alphaforge_llm.providers.cerebras import CerebrasAdapter

cer = CerebrasAdapter()
h = await cer.health()
print("Cerebras health:", h)
if h.available:
    r = await cer.complete(QUERY)
    print(f"Model: {r.model}  tokens: {r.prompt_tokens}+{r.completion_tokens}")
    print(r.content[:300])

# %% [markdown]
# ## 4. Gemini — direct call

# %%
from alphaforge_llm.providers.gemini import GeminiAdapter

gem = GeminiAdapter()
h = await gem.health()
print("Gemini health:", h)
if h.available:
    r = await gem.complete(QUERY)
    print(f"tokens: {r.prompt_tokens}+{r.completion_tokens}")
    print(r.content[:300])

# %% [markdown]
# ## 5. Mistral — direct call

# %%
from alphaforge_llm.providers.mistral import MistralAdapter

mis = MistralAdapter()
h = await mis.health()
print("Mistral health:", h)
if h.available:
    r = await mis.complete(QUERY)
    print(r.content[:300])

# %% [markdown]
# ## 6. DeepSeek — direct call

# %%
from alphaforge_llm.providers.deepseek import DeepSeekAdapter

ds = DeepSeekAdapter()
h = await ds.health()
print("DeepSeek health:", h)
if h.available:
    r = await ds.complete(QUERY)
    print(r.content[:300])

# %% [markdown]
# ## 7. Gateway — auto-routing by QueryType

# %%
gw = create_gateway()
for qt in [QueryType.FACTOID, QueryType.NEWS_LOOKUP, QueryType.STOCK_PICK]:
    try:
        r = await gw.complete(QUERY, query_type=qt)
        print(f"{qt.value:<22} → {r.provider:<12} {r.model}")
    except Exception as e:
        print(f"{qt.value:<22} → ERROR: {e}")

# %% [markdown]
# ## 8. CostGuard — Claude blocked without confirmation

# %%
from alphaforge_llm.providers.claude_sdk import ClaudeSdkAdapter

claude = ClaudeSdkAdapter()
try:
    gw2 = create_gateway()
    # Force claude-sdk by patching available set — gateway blocks it
    gw2._guard.check("claude-sdk", confirmed=False)
    print("ERROR: should have raised CostGuardError")
except CostGuardError as e:
    print(f"CostGuard correctly blocked: {e}")

# %% [markdown]
# ## 9. Router — chain inspection

# %%
router = QueryRouter()
for qt in QueryType:
    print(f"{qt.value:<22} {router.chain_for(qt)}")

# %% [markdown]
# ## 10. Rate limiter state

# %%
from alphaforge_llm.rate_limiter import RateLimiter

rl = RateLimiter()
for name in REGISTRY:
    rem = rl.remaining(name)
    print(f"  {name:<14} {rem:.1f} tokens remaining" if rem is not None else f"  {name:<14} unlimited")
