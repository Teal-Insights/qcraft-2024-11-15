# Series dependency graph (docs + FormulaEvaluator)

Pedagogical Cytoscape explorer for an exported package. Recompute uses
**excel-grapher FormulaEvaluator** (and optionally the exported `Model`), not a
browser-side formula clone.

## What gets seeded into `dist/`

| Path | Role |
|------|------|
| `{package}/graph_api.py` | `bootstrap()` / `evaluate(backend=…)` |
| `{package}/graph_schema.py` | **Author** `NODES` / `EDGES` (scaffold) |
| `{package}/graph_formula_evaluator.py` | FormulaEvaluator over `tests/fixtures/*.xlsx` |
| `assets/graph/` | Cytoscape UI (`app.js` calls `/api/…`) |
| `scripts/serve_graph_api.py` | Local stdlib HTTP server |
| `scripts/write_graph_bootstrap.py` | Static `bootstrap.json` for docs paint |
| `scripts/check_graph_eval.py` | FormulaEvaluator vs export parity on defaults |
| `examples/tiny_dsa_graph_schema.py` | Full Tiny DSA reference schema |

## Author the schema (per workbook)

After export, edit `{package}/graph_schema.py`:

1. List every series id in `SERIES_IDS` (inputs + internals + outputs).
2. Build `NODES` with roles/kinds/keys and cell addresses from `data.*`.
3. Author `EDGES` as producer → consumer pairs (the series DAG).

Copy patterns from `examples/tiny_dsa_graph_schema.py` (or the committed
`py-tiny-dsa` export). Addresses should match binding `data_range` cells.

## Run locally

From `dist/` (workbook fixture under `tests/fixtures/`):

```bash
uv sync --group graph
uv run python scripts/serve_graph_api.py
# open http://127.0.0.1:8765/
```

```bash
uv run python scripts/write_graph_bootstrap.py   # optional static snapshot
uv run python scripts/check_graph_eval.py        # FE vs Model defaults
```

`GET /api/graph` and `POST /api/evaluate` default to FormulaEvaluator when
`excel-grapher` is installed.

## Docs homepage embed

The document-stage agent should add a short **Interactive dependency graph**
section on the landing page (iframe + link to `assets/graph/index.html`) and
declare Quarto `resources: [../assets/graph/**]`. Avoid long explanatory
blurbs under the heading — the viz is the explanation.
