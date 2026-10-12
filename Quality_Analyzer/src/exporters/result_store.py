from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


class ResultStore:
    """
    Persistent storage for project analysis results.

    Internally keeps one result per project_id.

    JSONL format:
        {"project_id": "...", ...}
        {"project_id": "...", ...}
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.results = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        """
        Load existing results from disk.
        """

        if not self.file_path.exists():
            return {}

        results = {}

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                try:
                    obj = json.loads(line)

                    project_id = obj["project_id"]

                    results[project_id] = obj

                except Exception as e:
                    print(
                        f"Skipping invalid JSONL entry: {e}"
                    )

        return results

    def exists(
        self,
        project_id: str
    ) -> bool:
        return project_id in self.results

    def get(
        self,
        project_id: str
    ) -> Dict[str, Any] | None:
        return self.results.get(project_id)

    def save(self, result) -> None:
        """
        Insert or merge a project result.
        """

        if hasattr(result, "to_dict"):
            payload = result.to_dict()
        else:
            payload = result

        project_id = payload["project_id"]

        if project_id not in self.results:
            self.results[project_id] = payload

        else:
            existing = self.results[project_id]

            for tool_name, tool_result in payload.get("tools", {}).items():

                if tool_name not in existing["tools"]:
                    existing["tools"][tool_name] = tool_result
                    continue

                existing_data = existing["tools"][tool_name]["data"]
                new_data = tool_result["data"]

                if "versions" in new_data:

                    existing_versions = existing_data.setdefault(
                        "versions",
                        {}
                    )

                    existing_versions.update(
                        new_data["versions"]
                    )

                else:
                    existing["tools"][tool_name] = tool_result

        self._flush()

    def update_tool(
        self,
        project_id: str,
        language,
        tool_name: str,
        tool_result: Dict[str, Any]
    ) -> None:
        """
        Update a single tool result.
        """

        if project_id not in self.results:

            self.results[project_id] = {
                "project_id": project_id,
                "language": language,
                "tools": {}
            }

        if "tools" not in self.results[project_id]:
            self.results[project_id]["tools"] = {}

        if "language" not in self.results[project_id]:
            self.results[project_id]["language"] = language

        self.results[project_id]["tools"][tool_name] = tool_result

        self._flush()

    def _flush(self) -> None:
        """
        Rewrite the JSONL file.
        """

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as f:

            for result in self.results.values():

                json.dump(
                    result,
                    f,
                    ensure_ascii=False
                )

                f.write("\n")

    def all(self):
        return self.results.values()

    def count(self) -> int:
        return len(self.results)