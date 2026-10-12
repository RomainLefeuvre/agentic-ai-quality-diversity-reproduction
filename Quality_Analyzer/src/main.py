from analyzers.sonar import SonarAnalyzer
from orchestrator import AnalysisOrchestrator
from exporters.result_store import ResultStore 
from config import Config


def main():

    # Validate config ONCE (not os.getenv here)
    required = [
        Config.SONAR_URL,
        Config.SONAR_TOKEN,
        Config.SONAR_SCANNER_PATH
    ]

    if any(v is None for v in required):
        raise RuntimeError("Missing required environment variables")

    # Initialize analyzers
    analyzers = [
        SonarAnalyzer(
            sonar_url=Config.SONAR_URL,
            token=Config.SONAR_TOKEN,
            scanner_path=Config.SONAR_SCANNER_PATH
        ),
        
    ]

    orchestrator = AnalysisOrchestrator(analyzers)

    store = ResultStore(
        Config.OUTPUT_FILE
    )

    projects = orchestrator.discover_projects(Config.PROJECTS_DIR)

    print(f"Found {len(projects)} projects")

    for project in projects:
        
        print(f"Analyzing: {project.name}")

        result = orchestrator.analyze_project(project)

        store.save(result)

        print(f"Finished: {project.name}")

    print("Analysis complete")


if __name__ == "__main__":
    main()