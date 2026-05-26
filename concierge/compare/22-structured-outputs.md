# 22 — Structured Outputs / JSON Mode

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Native structured outputs / JSON schema mode per provider where supported; Pydantic models everywhere | Free |
| **Chosen** | **Pydantic models as the single source of truth. Native JSON-mode for Gemini and Groq. `Instructor` library as a thin wrapper for providers without first-class support. Strict validation; retry on parse failure (max 2 retries with the parse error fed back).** | Free |

---

## Context

Tool calls, plan steps, fact extraction, intent classification, verifier output — all of these need the LLM to produce structured data, not prose. Free-text parsing is brittle (regex over LLM output is a known failure mode). SOTA 2026 means native JSON/schema-mode on every major provider.

## Options

### A. Free-text + regex parsing

LLM outputs prose; we regex-extract fields. The bad old way.

### B. JSON-in-prose

System prompt asks for JSON inside a markdown code block. Parse the code block. Better, still fragile.

### C. Native JSON mode (no schema)

Provider guarantees output is valid JSON but doesn't enforce schema. The model can return any JSON shape.

### D. Native structured outputs (with schema)

Provider enforces a JSON schema at decode time — output is guaranteed-valid against the schema.

### E. Library-mediated (Instructor / Outlines)

Library handles provider-specific quirks, retries on validation failure, exposes a unified API.

## Provider support (as of 2026)

| Provider | Free-text | JSON mode | Schema-constrained |
|---|---|---|---|
| **Gemini 2.0+ Flash** | Yes | Yes (`response_mime_type: application/json`) | Yes (`response_schema`) |
| **Groq** (Llama 3.3) | Yes | Yes (`response_format: json_object`) | Partial (via tool calling abuse) |
| **Cerebras** | Yes | Yes | Limited |
| **DeepSeek R1** | Yes | Yes | Limited |
| **Anthropic** | Yes | Tool use as proxy | Via tool use input schemas |
| **Ollama local models** | Yes | Yes (most) | Some (Llama 3, Qwen 3 support `format: json`) |

## Recommendation

**Pydantic models as the contract; native schema where available; Instructor as the cross-provider adapter.**

### Pydantic-first

Every structured output is a Pydantic model:

```python
class PlanStep(BaseModel):
    id: str
    description: str
    tools: list[str]
    tool_args: list[dict]
    depends_on: list[str]

class Plan(BaseModel):
    plan: list[PlanStep]
    final_intent: str
```

### Provider adapter via Instructor

```python
from instructor import from_anthropic, from_gemini, from_groq

# inside concierge_service
client = wrap_with_instructor(gateway_client)
plan: Plan = await client.chat.completions.create(
    model="reasoning",
    response_model=Plan,
    messages=...,
    max_retries=2,
)
```

Instructor handles:
- Schema → provider format conversion
- Retry on validation failure with the error fed back to the model
- Async support
- All major free providers

### When the provider doesn't support schema mode

Fall back to JSON-mode + Pydantic validation in our code:

```python
raw = await gateway.complete(model, messages, response_format={"type": "json_object"})
try:
    plan = Plan.model_validate_json(raw)
except ValidationError as e:
    # Retry once with error fed back
    messages.append({"role": "user", "content": f"That output failed validation: {e}. Please correct it."})
    raw = await gateway.complete(...)
    plan = Plan.model_validate_json(raw)
```

### When even JSON mode isn't available

Local small models (some Ollama variants). Fall back to JSON-in-prose with regex extraction. Document this as a degraded path.

## Where structured outputs are used

| Component | Pydantic model | Provider feature |
|---|---|---|
| Plan-execute loop ([17](17-agentic-loop.md)) | `Plan` with `PlanStep[]` | Schema-constrained |
| Tool calls ([19](19-tool-calling.md)) | Per-tool Pydantic input | Native tool calling |
| Fact extraction ([12](12-long-term-memory.md)) | `list[ExtractedFact]` | Schema-constrained |
| Intent classification (if upgraded from regex to LLM) ([07](07-intent-classification.md)) | `IntentLabel` enum | Schema-constrained |
| Verifier pass ([25](25-verifier-pass.md)) | `VerificationResult` with claim-by-claim flags | Schema-constrained |
| Session summary | `SessionSummary` (free-text fields but bounded) | JSON mode |

## Validation strictness

| Field type | Validation |
|---|---|
| Enums (intent label, category) | Strict — model output must match an allowed value |
| Numeric ranges (confidence 0–1) | Strict — `confloat(ge=0, le=1)` |
| Free-text strings (descriptions) | Length capped; whitespace stripped |
| References between fields (depends_on → step ids) | Custom validator; reject orphan references |

Pydantic v2 handles all of this in the model definition.

## Performance impact

Schema-constrained decoding is sometimes slower than free decoding (provider-side constraint solving). Measured impact on Gemini Flash: negligible (<5% latency increase). On Groq: negligible. Worth using everywhere it's supported.

## Test strategy

For each structured-output path:

1. **Unit test**: feed fake LLM output (valid JSON matching schema) → assert correct Pydantic instance.
2. **Unit test**: feed malformed output → assert specific validation error.
3. **Integration test**: round-trip a real call (with cheap fast model) and assert the response validates.

Saved fake outputs live in `backend/tests/concierge/fixtures/llm_outputs/` for snapshot-style stability.

## Open questions

- **JSON schema feature parity**: which providers fully implement JSON Schema vs a subset? Gemini supports a subset (no `oneOf`, no nested `$ref`). Pydantic models that depend on these features need flattening. Document per-provider gotchas in a `compatibility.md`.
- **Error feedback prompt template**: when retrying after validation failure, what message gets sent? Test a few templates ("you returned X but the schema requires Y") for which yields highest retry success rate.
- **Streaming structured outputs**: some providers stream partial JSON. Worth using for the plan step so the UI shows the plan being built in real-time. Defer to v1.3.
- **Schema versioning**: when we add a field to `Plan`, models trained pre-change might omit it. Use `Optional` defaults aggressively; reject only on truly required fields.
- **Token cost of schema in prompt**: Gemini's `response_schema` is sent in the request; counts toward input tokens. Keep schemas compact; favor `Literal` enums over wide string fields.
