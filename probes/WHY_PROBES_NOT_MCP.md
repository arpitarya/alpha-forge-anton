# Why We Use Probes Instead of MCP for UI Verification

## What Is an MCP Tool?

MCP (Model Context Protocol) tools are server-based integrations that expose capabilities to Claude Code as structured function calls. The **Playwright MCP** is a common example: it lets Claude control a browser by calling tools like `browser_navigate`, `browser_click`, `browser_screenshot`, etc., all through the MCP protocol.

MCP tools run in a **separate process managed by Claude Code**, not inside the project. They are great for general-purpose tasks where you don't need project-specific context.

## What Is a Probe?

A probe is a **Python script inside this project** (`probes/`) that uses Playwright directly via `async` Python code. It attaches to the existing Chrome session via CDP (Chrome DevTools Protocol) on port 9299 — the same session already open for broker scraping (Zerodha, Groww, etc.).

Each probe is a standalone, runnable script:

```
uv run python probes/ui_probe.py
just ui-probe
```

## The Core Difference

| | Playwright MCP | Probes (`probes/`) |
|---|---|---|
| **Who runs it** | Claude Code harness | You (or `just`) |
| **What controls the browser** | MCP server, generic tool calls | Python script with full access to project internals |
| **Access to app internals** | None — black box | Full: can import `app.modules`, read env vars, call the API with real JWT tokens |
| **Browser session** | Opens a new isolated browser | Attaches to the existing AlphaForge Chrome via CDP `:9299` |
| **Test granularity** | Navigation and screenshot only | Auth flow, API response validation, per-broker data quality checks, pnl consistency |
| **Runs in CI / `just`** | No (requires Claude) | Yes — `just ui-probe` |
| **Reproducible without Claude** | No | Yes |

## Why Probes Win for AlphaForge Anton

### 1. CDP session reuse

AlphaForge's broker scrapers (Zerodha, Groww, etc.) already require a logged-in Chrome attached via CDP on port 9299. Probes reuse that same session — there's nothing extra to set up.

### 2. Project-aware assertions

`ui_probe.py` doesn't just check if a page loads. It:
- Reads the JWT from `localStorage` and hits `/api/portfolio/holdings` with it
- Validates that `pnl_pct` is mathematically consistent with `invested` / `current_value`
- Checks that no broker has holdings with `last_price = 0`

None of this is possible through generic MCP tool calls, which only see the DOM.

### 3. Deterministic, auditable, version-controlled

The probe is a Python file checked into the repo. Its assertions are explicit and reviewable in code review. MCP tool call sequences live only in Claude's conversation and vary run-to-run.

### 4. Runs without Claude

Any developer (or CI) can run `just ui-probe` to verify the UI independently of Claude Code. MCP requires an active Claude session.

### 5. No permission prompt noise

Every MCP browser tool call surfaces a permission prompt in the Claude Code UI. Probes run as a single `uv run` subprocess — one approval, full run.

## When MCP Would Be Fine

- Ad-hoc one-off exploration ("what does this third-party page look like?")
- Tasks with no project internals needed
- When you don't have a running CDP Chrome session

For AlphaForge Anton, those cases don't apply. The project has a persistent Chrome session and needs project-aware assertions — probes are the right tool.

## The Rule

> **Always use `probes/ui_probe.py` (CDP :9299) for all AlphaForge UI verification work. Never use Playwright MCP.**

This is documented in the project memory at `~/.claude/projects/…/memory/feedback_ui_probe_first.md`.
