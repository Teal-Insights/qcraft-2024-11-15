FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml README.md ./
COPY qcraft ./qcraft
COPY bindings ./bindings
COPY tests/fixtures/qcraft-toolv10.xlsx ./tests/fixtures/qcraft-toolv10.xlsx
COPY assets/graph ./assets/graph
COPY scripts/serve_graph_api.py ./scripts/serve_graph_api.py

# FormulaEvaluator needs the workbook, bindings, and excel-grapher (a project dep).
# Build the dependency graph into the image so the container loads it instead of
# recomputing 200k+ nodes before it can pass the healthcheck.
RUN uv pip install --system --no-cache . \
    && python -c "from qcraft.graph_formula_evaluator import warm; print(warm())"

ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

CMD ["python", "scripts/serve_graph_api.py"]
