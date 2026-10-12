from __future__ import annotations

import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import math
import requests
import re
from utils import parse_project_identity
from analyzers.base import Analyzer


class SonarAnalyzer(Analyzer):
    """
    SonarQube analyzer implementation.

    Responsibilities:
        - Run sonar-scanner
        - Wait for analysis completion
        - Retrieve metrics
        - Retrieve issues
        - Retrieve quality gate status
    """

    DEFAULT_METRICS = [
        "ncloc",
        "complexity",
        "cognitive_complexity",
        "bugs",
        "vulnerabilities",
        "security_hotspots",
        "code_smells",
        "duplicated_lines_density", 
        "sqale_index",
        "sqale_rating",
        "reliability_rating",
        "security_rating", 
        "comment_lines_density",
        "functions",
        "classes",
        "files",
        "statements",
    ]

    def __init__(
        self,
        sonar_url: str,
        token: str,
        scanner_path: str = "sonar-scanner",
        timeout: int = 3600,
        metrics: List[str] | None = None,
    ):
        self.sonar_url = sonar_url.rstrip("/")
        self.token = token
        self.scanner_path = scanner_path
        self.timeout = timeout
        self.metrics = metrics or self.DEFAULT_METRICS

    @property
    def name(self) -> str:
        return "sonarqube"

    def analyze(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze a project and return SonarQube results.

        Parameters
        ----------
        project_path : str
            Path to the source code project.

        Returns
        -------
        dict
            SonarQube analysis results.
        """
        print(f"Starting SonarQube analysis for {project_path}")
        project_path = Path(project_path).resolve()
        project_key, project_version = parse_project_identity(
            project_path.name
        )
        project_key = _sanitize_project_key(project_key)

        if self.project_version_exists(project_key, project_version):
            print(f"{project_key} already exists in SonarQube")
            return self._fetch_existing_results(project_key, project_version)
        else:
            report_file = self._run_scan(
                project_path=project_path,
                project_key=project_key,
                project_version=project_version,
            )

        task_id = self._extract_task_id(report_file)

        self._wait_for_completion(task_id)

        return {
            "status": "success",
            "project_key": project_key,
            "languages": self._fetch_languages(project_key),
            "versions": {
                project_version: {
                    "metrics": self._fetch_metrics(project_key),
                    "issues": self._fetch_issue_summary(project_key),
                    "quality_gate": self._fetch_quality_gate(project_key),
                }
            }
        }

        

    def _fetch_languages(self, project_key: str) -> List[str]:

        response = requests.get(
            f"{self.sonar_url}/api/components/tree",
            auth=(self.token, ""),
            params={
                "component": project_key,
                "qualifiers": "FIL",
                "ps": 500,
            },
        )

        response.raise_for_status()

        components = response.json().get("components", [])

        languages = {
            component["language"]
            for component in components
            if component.get("language")
        }

        return sorted(languages)

      # Scanner Execution
    

    def _run_scan(
        self,
        project_path: Path,
        project_key: str, project_version: str | None,
    ) -> Path:

        empty_binaries = project_path / "empty-binaries"
        empty_binaries.mkdir(exist_ok=True)

        cmd = [
            self.scanner_path,
            f"-Dsonar.projectKey={project_key}",
            f"-Dsonar.projectName={project_key}", 
            "-Dsonar.sources=.",
            f"-Dsonar.host.url={self.sonar_url}",
            f"-Dsonar.token={self.token}",
            f"-Dsonar.scm.disabled=true",
            f"-Dsonar.java.binaries={empty_binaries}",
        ]

        if project_version:
            cmd.append(
                f"-Dsonar.projectVersion={project_version}"
            )

        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
        )

        print("===== SONAR STDOUT =====")
        print(result.stdout)

        print("===== SONAR STDERR =====")
        print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                f"SonarScanner failed for '{project_key}'\n\n"
                f"STDOUT:\n{result.stdout}\n\n"
                f"STDERR:\n{result.stderr}"
            )

        report_file = (
            project_path
            / ".scannerwork"
            / "report-task.txt"
        )

        if not report_file.exists():
            raise FileNotFoundError(
                f"Could not locate {report_file}"
            )

        return report_file

      # Compute Engine Monitoring
    

    def _extract_task_id(self, report_file: Path) -> str:

        with open(report_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ceTaskId="):
                    return line.strip().split("=", 1)[1]

        raise RuntimeError(
            "Unable to find ceTaskId in report-task.txt"
        )

    def _wait_for_completion(self, task_id: str):

        start_time = time.time()

        while True:

            elapsed = time.time() - start_time

            if elapsed > self.timeout:
                raise TimeoutError(
                    f"SonarQube analysis exceeded "
                    f"{self.timeout} seconds."
                )

            response = requests.get(
                f"{self.sonar_url}/api/ce/task",
                auth=(self.token, ""),
                params={"id": task_id},
            )

            response.raise_for_status()

            status = response.json()["task"]["status"]

            if status == "SUCCESS":
                return

            if status in ("FAILED", "CANCELED"):
                raise RuntimeError(
                    f"Analysis failed with status '{status}'."
                )

            time.sleep(3)

      # SonarQube API
    

    def _fetch_metrics(
        self,
        project_key: str,
    ) -> Dict[str, Any]:

        response = requests.get(
            f"{self.sonar_url}/api/measures/component",
            auth=(self.token, ""),
            params={
                "component": project_key,
                "metricKeys": ",".join(self.metrics),
            },
        )

        response.raise_for_status()

        data = response.json()

        metrics = {}

        for measure in data["component"]["measures"]:

            value = measure.get("value")

            if value is not None:
                try:
                    value = float(value)

                    if value.is_integer():
                        value = int(value)

                except ValueError:
                    pass

            metrics[measure["metric"]] = value

        return metrics



    def _fetch_issues(
        self,
        project_key: str,
    ) -> List[Dict[str, Any]]:

        issues = []

        page_size = 500

        response = requests.get(
            f"{self.sonar_url}/api/issues/search",
            auth=(self.token, ""),
            params={
                "projects": project_key,
                "p": 1,
                "ps": page_size,
            },
        )

        if response.status_code != 200:
            print("STATUS:", response.status_code)
            print("URL:", response.url)
            print("BODY:", response.text)
            response.raise_for_status()

        data = response.json()

        issues.extend(data.get("issues", []))

        paging = data.get("paging", {})

        total = paging.get("total", 0)

        num_pages = math.ceil(total / page_size)

        for page in range(2, num_pages + 1):

            response = requests.get(
                f"{self.sonar_url}/api/issues/search",
                auth=(self.token, ""),
                params={
                    "projects": project_key,
                    "p": page,
                    "ps": page_size,
                },
            )

            if response.status_code != 200:
                print("\n==============================")
                print("PROJECT:", project_key)
                print("PAGE:", page)
                print("STATUS:", response.status_code)
                print("URL:", response.url)
                print("BODY:", response.text)
                print("==============================\n")

                response.raise_for_status()

            issues.extend(
                response.json().get("issues", [])
            )

        return issues
    
    def _fetch_issue_summary(
        self,
        project_key: str,
    ) -> Dict[str, Any]:

        response = requests.get(
            f"{self.sonar_url}/api/issues/search",
            auth=(self.token, ""),
            params={
                "projects": project_key,
                "p": 1,
                "ps": 500,
            },
        )

        response.raise_for_status()

        data = response.json()

        paging = data.get("paging", {})
        total = paging.get("total", 0)

        summary = {
            "total": total,
            "by_type": {},
            "by_severity": {},
        }

        page_size = 500
        max_results = 10000

        num_pages = min(
            math.ceil(total / page_size),
            math.ceil(max_results / page_size)
        )

        for page in range(1, num_pages + 1):

            if page > 1:

                response = requests.get(
                    f"{self.sonar_url}/api/issues/search",
                    auth=(self.token, ""),
                    params={
                        "projects": project_key,
                        "p": page,
                        "ps": page_size,
                    },
                )

                response.raise_for_status()

                data = response.json()

            for issue in data.get("issues", []):

                issue_type = issue.get(
                    "type",
                    "UNKNOWN"
                )

                severity = issue.get(
                    "severity",
                    "UNKNOWN"
                )

                summary["by_type"][issue_type] = (
                    summary["by_type"].get(
                        issue_type,
                        0
                    ) + 1
                )

                summary["by_severity"][severity] = (
                    summary["by_severity"].get(
                        severity,
                        0
                    ) + 1
                )

        summary["retrieved"] = min(
            total,
            max_results
        )

        summary["truncated"] = (
            total > max_results
        )

        return summary

    def _fetch_quality_gate(
        self,
        project_key: str,
    ) -> Dict[str, Any]:

        response = requests.get(
            f"{self.sonar_url}/api/qualitygates/project_status",
            auth=(self.token, ""),
            params={
                "projectKey": project_key,
            },
        )

        response.raise_for_status()

        return response.json()["projectStatus"]


    def project_version_exists(
    self,
    project_key: str,
    project_version: str | None
) -> bool:

        if project_version is None:
            return False

        response = requests.get(
            f"{self.sonar_url}/api/components/show",
            params={
                "component": project_key
            },
            auth=(self.token, "")
        )

        if response.status_code != 200:
            return False

        component = response.json()["component"]

        # Sonar stores the current project version here
        current_version = component.get("version")

        return current_version == project_version
    
    def _fetch_existing_results(self, project_key: str, project_version: str | None):
        version_data = {}

        try:
            version_data["metrics"] = self._fetch_metrics(project_key)
        except Exception as e:
            version_data["metrics_error"] = str(e)

        try:
            version_data["issues"] = self._fetch_issue_summary(project_key)
        except Exception as e:
            version_data["issues_error"] = str(e)

        try:
            version_data["quality_gate"] = self._fetch_quality_gate(project_key)
        except Exception as e:
            version_data["quality_gate_error"] = str(e)

        try:
            languages = self._fetch_languages(project_key)
        except Exception as e:
            languages = []
            version_data["languages_error"] = str(e)

        return {
            "status": "success",
            "project_key": project_key,
            "languages": languages,
            "versions": {
                project_version: version_data
            }
        }



def _sanitize_project_key(project_key: str) -> str:
    return re.sub(
        r"[^A-Za-z0-9_\-]",
        "_",
        project_key
    )
