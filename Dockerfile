FROM ghcr.io/astral-sh/uv:python3.11-alpine

RUN apk add --no-cache git

WORKDIR /app

COPY python/pyproject.toml python/uv.lock ./

RUN uv sync --frozen --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--no-browser", \
     "--allow-root", \
     "--notebook-dir=/workspace"]
