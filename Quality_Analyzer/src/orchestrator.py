from __future__ import annotations

from pathlib import Path
from typing import Iterable

from models.result_schema import (
    ProjectResult,
    ToolResult
)
from utils import parse_project_identity

class AnalysisOrchestrator:
    """
    Coordinates the execution of analyzers on projects.
    """

    def __init__(self, analyzers):
        self.analyzers = analyzers

    def analyze_project(
        self,
        project_path: str | Path
    ) -> ProjectResult:

        project_path = Path(project_path)

        project_id, project_version = parse_project_identity(
            project_path.name
        )

        result = ProjectResult(
            project_id=project_id,
            language=""
        )

        for analyzer in self.analyzers:

            try:
                analyzer_result = analyzer.analyze(str(project_path))

                if analyzer.name == "sonarqube":
                    languages = analyzer_result.get("languages", [])

                    if languages:
                        result.language = languages[0]

                result.add_tool_result(
                    analyzer.name,
                    ToolResult(
                        status="success",
                        data=analyzer_result
                    )
                )

            except Exception as e:

                result.add_tool_result(
                    analyzer.name,
                    ToolResult(
                        status="failed",
                        data={
                            "error": str(e)
                        }
                    )
                )

        return result

    def analyze_projects(
        self,
        projects: Iterable[str | Path]
    ):

        for project in projects:
            yield self.analyze_project(project)

    @staticmethod
    def discover_projects(
        root_directory: str | Path
    ) -> list[Path]:
        """
        Returns all first-level directories
        under a root folder.

        Example:

        projects/
        ├── repo1/
        ├── repo2/
        └── repo3/

        returns:
            [repo1, repo2, repo3]
        """

        root_directory = Path(root_directory)

        return sorted(
            [
                p
                for p in root_directory.iterdir()
                if p.is_dir()
            ]
        )
    
