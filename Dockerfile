FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml README.md ./
COPY qcraft ./qcraft
COPY assets/graph ./assets/graph
COPY scripts/serve_graph_api.py ./scripts/serve_graph_api.py

# Export-backend viz only needs the installed package (Model + data).
RUN uv pip install --system --no-cache .

ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

CMD ["python", "scripts/serve_graph_api.py"]
