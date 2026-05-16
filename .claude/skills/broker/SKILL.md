---
name: broker
description: "Add, edit, or remove a broker source in AlphaForge (registry, module files, fixtures, docs)"
trigger: /broker
---

# /broker

Manage AlphaForge broker sources. Understands the full module layout, registry wiring, fixture CSVs, and docs.

## Usage

```
/broker list                        # Show registered brokers + their kind/status
/broker add <slug>                  # Scaffold a new broker module
/broker edit <slug>                 # Edit an existing broker's CSV parser, source, or helper
/broker remove <slug>               # Remove a broker (module + registry + fixtures)
```

## What You Must Do When Invoked

Read these files first — they are authoritative:
- `docs/broker-source-integration.md` — full architecture, templates, checklist
- `docs/broker-csv-dumps.md` — dump_utils contract, CSV format
- `backend/app/modules/brokers/registry.py` — current registered sources

---

### /broker list

Read `backend/app/modules/brokers/registry.py` and list every registered source with its slug, label, and `SourceKind`. Also show what files exist under `backend/app/modules/brokers/`.

---

### /broker add <slug>

**Step 1 — Gather requirements**

Ask the user (one question, wait for the answer):

> What kind of source is **{slug}**?
> - **CSV** — user exports a file and uploads it (simplest, no auth)
> - **API (CDP)** — backend attaches to Chrome over CDP, scrapes the authenticated page

Then ask what asset class(es) it holds (EQUITY / MUTUAL_FUND / BOND / GOLD / ETF / OTHER) and what the known CSV column headers look like (if CSV kind).

**Step 2 — Create module files**

Create `backend/app/modules/brokers/{slug}/` with these files. Follow the 100-line limit per file (50 for `*_csv.py`).

#### For a CSV-only source

Create exactly these files:

**`{slug}_csv.py`** — the BrokerSource (slug={slug}, kind=CSV, implements parse()):

- Use `_csv_helper.pick()` with 3-5 column name aliases per field (import, purchase price, avg buy, etc.) — CSVs vary between export versions.
- Detect `asset_class` from a "Type" or "Category" column when the source holds multiple asset classes; default to the primary one.
- Mirror the pattern in `groww_csv.py` or `angelone_csv.py`.

**`__init__.py`** — barrel export only:
```python
from app.modules.brokers.{slug}.{slug}_csv import {Slug}CSVSource
__all__ = ["{Slug}CSVSource"]
```

#### For an API (CDP) source

Create all six files listed in `docs/broker-source-integration.md`:
- `__init__.py`
- `{slug}_source_helper.py` — REQUIRED_ENV, `acquire_token()`, `fetch_holdings_json()`
- `{slug}_dump.py` — TTL wrappers (copy template from docs, replace slug)
- `{slug}_source.py` — BrokerSource subclass (kind=API), `fetch()` + `parse()` delegation
- `{slug}_csv.py` — CSV-upload parser fallback

Use the templates verbatim from `docs/broker-source-integration.md` — replace `mybroker`/`MyBroker` with the actual slug/class name.

**Step 3 — Wire into registry**

Edit `backend/app/modules/brokers/registry.py`:
- Add the import at the top (alphabetical by module path).
- Add `{Slug}Source()` or `{Slug}CSVSource()` to the `instances` list.

**Step 4 — Update dev_brokers.py**

Add `"{slug}": "{slug}_holdings.csv"` to `FIXTURE_MAP` in `backend/scripts/dev_brokers.py`.

**Step 5 — Add a fixture CSV**

Create `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` with 3-5 representative rows using the column headers the user described. Cover at least two asset classes if the source holds multiple.

**Step 6 — Docs update**

In `docs/broker-source-integration.md`:
- Add a `## {Label} ({slug})` section after Angel One with the slug, auth kind, REQUIRED_ENV (if API), asset classes, and field mapping.
- Add the broker to the Dev notebooks table (even if the notebook doesn't exist yet — mark it TBD).
- If API kind, add a probe script entry to the XHR Probes table.

**Step 7 — Confirm**

Print the list of files created/modified and the new registry line. Tell the user what to do next (upload a CSV, or set env vars and log in to Chrome).

---

### /broker edit <slug>

**Step 1 — Read current state**

Read all files in `backend/app/modules/brokers/{slug}/`. Also read the relevant section of `docs/broker-source-integration.md`.

**Step 2 — Ask what to change**

Ask:
> What do you want to change in **{slug}**?
> - CSV column aliases (the `pick()` calls in `{slug}_csv.py`)
> - Asset-class detection logic
> - Auth / env vars (`{slug}_source_helper.py`)
> - CDP endpoint or field mapping
> - Notes / label
> - Something else

**Step 3 — Apply the edit**

Make the minimum change. Don't touch unrelated files. Keep line budgets (100 / 50).

After editing the CSV parser, verify the fixture CSV at `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` still matches the updated column aliases — update it if not.

**Step 4 — Docs**

Update the `## {Label}` section in `docs/broker-source-integration.md` to reflect the change (field mapping, env vars, etc.).

---

### /broker remove <slug>

**Step 1 — Confirm**

Tell the user exactly what will be deleted and ask for confirmation before touching anything.

**Step 2 — Remove**

After confirmation:
1. Delete `backend/app/modules/brokers/{slug}/` (entire directory).
2. Remove the import and instance line from `backend/app/modules/brokers/registry.py`.
3. Remove the entry from `FIXTURE_MAP` in `backend/scripts/dev_brokers.py`.
4. Delete `backend/tests/fixtures/broker_csvs/{slug}_holdings.csv` if it exists.
5. Delete `probes/{slug}_probe.py` if it exists.

**Step 3 — Docs**

In `docs/broker-source-integration.md`:
- Remove the `## {Label} ({slug})` section entirely.
- Remove the broker from the Dev notebooks table and XHR Probes table.

**Step 4 — Confirm**

List every deleted file and every line removed from registries/docs.

---

## Rules

- Never exceed 100 lines per source file, 50 lines per `*_csv.py`.
- Never reimplement `dump_utils` path/CSV logic — always import from `app.modules.brokers.dump_utils`.
- Use `app.modules.brokers._csv_helper.pick()` for all CSV column picking — never `row.get()` directly.
- All `parse()` methods must call `to_float()` for every numeric field (handles empty strings).
- `pnl_pct` must always use `(pnl / invested * 100) if invested else 0.0` to avoid ZeroDivisionError.
- Every code change must be accompanied by a doc update in the same session (project rule).
- Filenames: `{slug}_{role}.py` — no other pattern.
