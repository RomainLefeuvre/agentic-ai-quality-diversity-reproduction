from dataclasses import dataclass, field
from typing import Optional


# FUNCTION-LEVEL STRUCTURES
@dataclass
class Parameter:
    name: str
    type: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class CodeBlock:
    raw: str
    normalized: str


@dataclass
class Metrics: # We will add more metrics as needed
    loc: int
    token_count: int 


@dataclass
class Hashes:
    raw_sha256: str
    normalized_sha256: str


@dataclass
class Function:
    function_id: str

    name: str
    qualified_name: str

    class_name: Optional[str]

    signature: str

    parameters: list[Parameter] = field(default_factory=list)

    return_type: Optional[str] = None

    modifiers: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)

    is_async: bool = False
    is_static: bool = False

    start_line: int = 0
    end_line: int = 0

    code: Optional[CodeBlock] = None
    metrics: Optional[Metrics] = None
    hashes: Optional[Hashes] = None



# SOURCE FILE
@dataclass
class SourceFile:
    source_id: str

    file_name: str
    relative_path: str

    package: Optional[str]
    qualified_name: Optional[str]

    imports: list[str] = field(default_factory=list)

    functions: list[Function] = field(default_factory=list)



# PROJECT-LEVEL STRUCTURES
@dataclass
class ProjectMetadata:
    name: str
    language: str
    repository_url: str


@dataclass
class ProjectEntry:
    entry_id: str

    project: ProjectMetadata

    sources: list[SourceFile] = field(default_factory=list)