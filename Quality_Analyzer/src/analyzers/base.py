from abc import ABC, abstractmethod

class Analyzer(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def analyze(self, project_path: str) -> dict:
        pass