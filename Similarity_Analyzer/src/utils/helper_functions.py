from pathlib import Path
import hashlib, json, uuid, json

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".cs": "csharp"
}


IGNORED_DIRECTORIES = {
    ".git",
    "venv",
    "__pycache__",
    "node_modules",
    "bin",
    "obj",
    "target"
}


def detect_language(project_root: Path) -> str:
    counts = {}

    for ext, lang in SUPPORTED_EXTENSIONS.items():
        counts[lang] = len(list(project_root.rglob(f"*{ext}")))

    return max(counts, key=counts.get)


def iter_source_files(project_root: Path, language: str):

    language_to_extension = {
        "python": ".py",
        "java": ".java",
        "csharp": ".cs"
    }

    extension = language_to_extension[language]

    for path in project_root.rglob(f"*{extension}"):

        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue

        yield path


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def stable_id(value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))



def load_existing_entry_ids(jsonl_path):
    jsonl_path = Path(jsonl_path) 
    if not jsonl_path.exists():
        return set()

    ids = set()

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                ids.add(obj.get("entry_id"))
            except json.JSONDecodeError:
                continue

    return ids

def print_banner():

    banner = r"""
========================================================
   CODE HISTORIAN FUNCTION EXTRACTOR
========================================================

  Multi-language Dataset Extraction Pipeline
  Supported Languages:
    - Python
    - Java
    - C#

========================================================
"""

    print(banner)




def get_language_from_jsonl(csv_file: str) -> str:
    csv_path = Path(csv_file)

    # remove "_pairs.csv"
    jsonl_path = csv_path.parent / csv_path.name.replace("_pairs.csv", ".jsonl")

    if not jsonl_path.exists():
        print(f"Metadata file not found: {jsonl_path}")
        return "unknown"

    with open(jsonl_path, "r", encoding="utf-8") as f:
        entry = json.loads(f.readline())

    return entry.get("project", {}).get("language", "unknown")