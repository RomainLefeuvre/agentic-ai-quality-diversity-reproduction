# gen-ai-clone-study

Study of AI-generated code clones in popular open-source repositories, using the [Software Heritage](https://www.softwareheritage.org/) graph dataset.



### Output files

| File | Description |
|---|---|
| `output/origins.parquet` | Raw origin metadata from the SWH graph |
| `output/root_edges.parquet` | Root-commit edges used to detect forks |
| `output/fork_enrichment.parquet` | Fork count and `is_fork` flag per origin |
| `output/passing_origins.parquet` | Origins that pass all quality filters (132 repos) |
| `output/sources/` | Downloaded source trees (~10 GB) |

## Requirements

Choose one of two options:

- **uv** (recommended) — [install uv](https://docs.astral.sh/uv/getting-started/installation/), then follow the [uv setup](#setup-with-uv) instructions below.
- **Docker** — no local Python setup needed; follow the [Docker setup](#setup-with-docker) instructions below.

---

## Setup with uv

```bash
cd python/
uv sync
```

Then create a `.env` file from `.env.example` and set your tokens:

```
SWH_TOKEN=<your Software Heritage API token>
GITHUB_TOKEN=<optional, used as fallback source>
```

### Usage

Open Jupyter and run `download_sample.ipynb`:

```bash
cd python/
uv run jupyter lab --notebook-dir ..
```

---

## Setup with Docker

Create a `.env` file from `.env.example` and set your tokens:

```
SWH_TOKEN=<your Software Heritage API token>
```

### Usage

```bash
docker compose up --build
```

Open the URL printed in the terminal (e.g. `http://127.0.0.1:8888/lab?token=...`) and run `download_sample.ipynb`.

> The current directory is mounted at `/workspace` inside the container, so output files are written directly to your local `output/` folder.

---

The notebook reads `passing_origins.parquet`, selects the top 50 origins with a resolved HEAD commit, and downloads their source trees into `output/sources/`.

---

## Getting API tokens

### Software Heritage token (required)

1. [Create a Software Heritage account](https://archive.softwareheritage.org/oidc/login/)
2. Once logged in, go to your [profile token page](https://archive.softwareheritage.org/oidc/profile/#tokens) and generate a new token.
3. Copy the token into your `.env` file as `SWH_TOKEN`.

