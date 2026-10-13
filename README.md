# From LLM Assistance to Agentic AI: An Empirical Study of Source Code Similarity, Quality, and Structural Growth




Reproduction package for 

```
From LLM Assistance to Agentic AI: An Empirical Study
of Source Code Similarity, Quality, and Structural Growth
Luciano Marchezan ⋅ Romain Lefeuvre ⋅ Kevin Delcourt ⋅
Benoit Combemale ⋅ Houari Sahraoui
```


## Dataset extraction


### Requirements

- **uv** (recommended) — [install uv](https://docs.astral.sh/uv/getting-started/installation/), then follow the [uv setup](#setup-with-uv) instructions below.

### Setup 

#### 0. Download submodule
```
git submodule update --init --recursive
```

#### 1. Initialize the workspace

```bash
cd python/
uv sync
```

### Stage 1 — Download the source list

Download `analysis_report_128575.csv` from [Zenodo](https://zenodo.org/records/19256968) and place it in `input/`.

### Stage 2 — Preprocess

Run the preprocessing notebook, `python/STAGE_2_agentic_usage_swh_preprocess.ipynb`, which aligns Software Heritage origins with the repository URLs from GitHub.

```bash
cd python/
uv run papermill STAGE_2_agentic_usage_swh_preprocess.ipynb executed.ipynb --log-output
```

### Stage 3 — Extract data from Software Heritage

This stage runs on Grid'5000 using the script and container image in this repository (`extract_metrics.sh`, deployed via `swherlock`).

Connect to the cluster:

```bash
ssh nancy.aba
oarsub -S .grid_5k_entrypoint
ssh grosminet.aba
```

Then run the extraction:

```bash
./extract_metrics.sh
```

If you are not on Grid'5000, you can skip the `ssh`/`oarsub` steps above and run the
`swh-extract` binary directly from the `swherlock` submodule (the source of the
`swh-filter` image used by `extract_metrics.sh`):

```bash
cd swherlock
cargo run --release --bin swh-extract -- \
  --graph <path/to/graph> \
  --output-dir <path/to/output> \
  --chunk-size 1000000 --threads 0 \
  --origin-urls <path/to/input/agentic_usage_swh.csv>
```

### Stage 4 — Apply sampling extraction

Run `python/STAGE_4_sample_extraction.ipynb`.

```bash
cd python/
uv run papermill STAGE_4_sample_extraction.ipynb executed.ipynb --log-output
```

### Stage 5 — Download the sample locally


| File | Description |
|---|---|
| `output/passing_origins_sample.parquet` | Filtered sample of origins, one row per repo, including a `yearly_head_revisions` column (list of `(date, swhid)` pairs, one per year for 2021,2024,2026) |
| `output/sources/<owner>_<repo>/2024/` | Source tree checked out at the repo's 2024 HEAD revision |
| `output/sources/<owner>_<repo>/2026/` | Source tree checked out at the repo's 2026 HEAD revision |




### 2. Configure tokens

Create a `.env` file from `.env.example` and set your tokens:

```
SWH_TOKEN=<your Software Heritage API token>
GITHUB_TOKEN=<optional, used as fallback source>
```

### Usage

Open Jupyter and run `STAGE_5_download_sample.ipynb`:

```bash
cd python/
uv run jupyter lab --notebook-dir ..
```

Or run directly from the CLI with papermill:

```bash
uv add papermill
cd python/
uv run papermill STAGE_5_download_sample.ipynb executed.ipynb --log-output
```

The same `papermill` command works for the other notebooks in `python/` — just swap the
input filename:

```bash
uv run papermill STAGE_2_agentic_usage_swh_preprocess.ipynb executed.ipynb --log-output
uv run papermill STAGE_4_sample_extraction.ipynb executed.ipynb --log-output
```

---

The notebook reads `passing_origins_sample.parquet` and, for each repo, downloads two independent source-tree snapshots — the HEAD revision closest to end of 2021, 2024 and 2026 (from the `yearly_head_revisions` column) — into `output/sources/<owner>_<repo>/2021/` ...

---

## Getting API tokens

### Software Heritage token (required)

1. [Create a Software Heritage account](https://archive.softwareheritage.org/oidc/login/)
2. Once logged in, go to your [profile token page](https://archive.softwareheritage.org/oidc/profile/#tokens) and generate a new token.
3. Copy the token into your `.env` file as `SWH_TOKEN`.

# Quality Analyzer

Check the README inside the Quality_Analyzer folder.

# Similarity Analyzer

Check the README inside the Similarity_Analyzer folder.
