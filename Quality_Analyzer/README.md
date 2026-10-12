# Quality Analyzer

A modular Python framework for analyzing software projects using SonarQube.
  
## Configuration (.env + Config class)

This project uses environment variables to configure runtime settings.

### 1. Create a `.env` file

Create a file named `.env` in the project root:

Example file is provided as:
 
### `.env.example`

```env
SONAR_URL=http://localhost:9000
SONAR_TOKEN=YOUR_TOKEN

SONAR_SCANNER_PATH=path/to/sonar-scanner/bin/sonar-scanner.bat 
```

---

### 2. Config Loader

All environment variables are loaded through `config.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    SONAR_URL = os.getenv("SONAR_URL")
    SONAR_TOKEN = os.getenv("SONAR_TOKEN")
    SONAR_SCANNER_PATH = os.getenv("SONAR_SCANNER_PATH") 
     
    PROJECTS_DIR = Path("../projects")
    OUTPUT_FILE = Path("../results/analysis_results.jsonl")
```


## Prerequisites

* Python 3.10+ is required for the pipeline
* Java 21+ is required for Sonar  

### SonarQube

A running [SonarQube](https://www.sonarsource.com/products/sonarqube/downloads/) instance with Sonar Scanner installed.

For Linux OS, follow the guide [here](https://docs.sonarsource.com/sonarqube-community-build/server-installation/pre-installation/linux)

Verify installation:

```bash
sonar-scanner --version
```

#### Generate an Access Token

```bash
cd sonarqube-version\bin\windows-x86-64
```

Run SonarQube 
```bash
 .\StartSonar.bat
 ```

Open the server at [http://localhost:9000](http://localhost:9000) 

In SonarQube:

```text
My Account -> Security
```
Give a name and select type to ```User Token```, then click ```Generate```

Save the generated token in the ```.env``` file.

---
## Installation 

Create a virtual environment: 
```bash 
python -m venv .venv 
```

Activate it: 

Linux/macOS: 
```bash
source .venv/bin/activate 
``` 
  
Windows: 
```bash
.venv\Scripts\activate
``` 

Install all dependencies: 
```bash
 pip install -r requirements.txt
 ``` 

 
## Running the Pipeline 

Make sure SonarQube server is running:
 
```bash
.\StartSonar.bat
 ```

 **Notice that due to the size of some projects, it is recommended to increase the memory heap size in the Sonar settings**


Run the pipeline inside ```src/```
```bash
python main.py
```

---

## Output

Results are stored in:

```text
results/analysis_results.jsonl
```

Example:

```json
{
  "project_id": "repo1",
  "timestamp": "2026-06-09T16:30:00",
  "tools": {
    "sonarqube": {
      "status": "success",
      "data": {
        "project_key": "repo1",
        "metrics": {
          "ncloc": 1350,
          "complexity": 240,
          "bugs": 1
        }
      }
    }
  }
}
```
## Results analysis

Results analysis can be run in 

```bash
analysis/data_analysis.ipynb
```
---


### Result Schema

File:

```text
models/result_schema.py
```

Defines:

- ToolResult
- ProjectResult

Example:

```json
{
  "project_id": "repo1",
  "timestamp": "2026-06-09T16:00:00",
  "tools": {
    "sonarqube": {
      "status": "success",
      "data": {
        "metrics": {}
      },
    }
  }
}
```
---

## Architecture

```text
src/
│
├── analyzers/
│   ├── __init__.py
│   ├── base.py 
│   └── sonar.py
│
├── exporters/
│   ├── __init__.py
│   └── jsonl_exporter.py
│
├── models/
│   ├── __init__.py
│   └── result_schema.py
│
├── orchestrator.py
├── config.py
├── main.py
│
projects/
results/
```

Place repositories to analyze under:

```text
projects/
├── repo1/
├── repo2/
├── repo3/
└── repoN/
```

Each directory is treated as a separate project.

---
