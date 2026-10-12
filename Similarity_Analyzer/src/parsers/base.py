from abc import ABC, abstractmethod
from pathlib import Path

from dataclasses import SourceFile


class BaseParser(ABC):

    @abstractmethod
    def extract(self, file_path: Path, project_root: Path) -> SourceFile:
        pass