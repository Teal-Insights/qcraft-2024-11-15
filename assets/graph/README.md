# Series dependency graph (docs + Model API)

Pedagogical Cytoscape explorer for Q-CRAFT. Recompute uses the exported
``qcraft.model.Model`` via ``GET/POST /api/…`` (FormulaEvaluator optional).

## Run locally

```bash
uv sync --group graph
uv run python scripts/write_graph_bootstrap.py   # static docs snapshot
uv run python scripts/check_graph_eval.py
uv run python scripts/serve_graph_api.py
# open http://127.0.0.1:8765/
```

Docs homepage embeds ``index.html?preview=1`` (read-only); click through to
the fullscreen interactive page.
