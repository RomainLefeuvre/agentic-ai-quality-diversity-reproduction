# Function Extractor & Similarity Evaluation Pipeline

A multi-language source code analysis pipeline for extracting functions from software repositories, generating function pairs, and evaluating code similarity (semantic similarity with Cosine Sim, and syntactic similarity with CodeBLEU).

## Requirements

```bash
pip install -r requirements.txt
```

Depending on your Python environment, additional packages may be required.

**Windows:** [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) are required by CodeBLEU. Install **Desktop development with C++**, including the Windows 10/11 SDK and C++ CMake tools.

## How to Run

The pipeline is executed through `src.main` and supports three modes:

- `extract` — function extraction only
- `pairs` — pair generation only
- `all` — full pipeline

### All projects

Pass a directory containing multiple project repositories:

```bash
python -m src.main repos --mode all
```

For multiple projects, the pipeline:

1. Extracts functions from each project into `output/<project>.jsonl`
2. Runs the diff pipeline
3. Generates function-pair CSV files from the diff (only added functions are considered)

### Single project

Run the full pipeline:

```bash
python -m src.main tests/calc-test --mode all
```

Run extraction only:

```bash
python -m src.main tests/calc-test --mode extract
```

Run pair generation:

```bash
python -m src.main tests/calc-test --mode pairs
```

### Clone detection

After generating the pair files:

```bash
python -m src.run_detection --csv-folder output/
```

Multiple models can be specified:

```bash
python -m src.run_detection \
    --csv-folder output/ \
    --models microsoft/codebert-base Salesforce/codet5-base
```

### Results

Results are saved in:
```text
results/
```

Analysis is available in:
```text
analysis/similarity_analysis.ipynb
analysis/qualitative_analysis.ipynb
```


### Options

```text
python -m src.main <project_path> [options]

--output <path>        Output JSONL file for a single project
--pairs-output <path>  Output directory/file for pairs
--entry-id <id>       Process only a specific entry
--mode <mode>         extract, pairs, or all
```

## Supported Languages

- Python
- Java 

Language is automatically detected based on source-file extensions:

| Extension | Language |
|-----------|----------|
| `.py` | Python |
| `.java` | Java | 

## Dataset Structure

The extraction pipeline produces JSONL data containing project, source-file, and function information.

```json
{
  "entry_id": "proj_000001",
  "project": {
    "name": "django",
    "language": "python",
    "repository_url": "https://github.com/django/django"
  },
  "sources": [
    {
      "source_id": "src_000001",
      "file_name": "request.py",
      "relative_path": "django/http/request.py",
      "package": "django.http",
      "functions": [
        {
          "function_id": "fn_000001",
          "name": "get_host",
          "qualified_name": "django.http.request.HttpRequest.get_host",
          "signature": "get_host(self)",
          "start_line": 120,
          "end_line": 148,
          "code": {
            "raw": "...",
            "normalized": "..."
          }
        }
      ]
    }
  ]
}
```

## Project Structure

```text
src/
├── main.py
├── extractor_pipeline.py
├── run_detection.py
├── config.py
├── utils/
│   ├── helper_functions.py
│   ├── create_function_pairs.py
│   ├── models.py
│   └── transformer_test_loader.py
├── parsers/
│   ├── base.py
│   └── python_parser.py
├── normalization/
│   └── serializer.py
├── clone_detection/
│   └── sentence_transformers_detector.py
└── embeddings/
    ├── codebert.py
    └── embeddings_calc.py

output/
results/
```

## Pipeline Overview

```text
Source repositories
        │
        ▼
Function extraction
        │
        ▼
Create a Project JSONL files
        │
        ▼
If multiple versions of the project exist, extracts the diff (only newly added functions)
        │
        ▼
Creates function-pair CSV files
        │
        ▼
Semantic and Syntactic similarity evaluation
```
