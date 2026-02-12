from dataclasses import dataclass
from typing import Protocol, Iterable, Optional, Union, Callable
from .vocab_helpers import normalize_default, compose_normalizers

@dataclass(frozen=True)
class ConceptRow:
    concept_id: int
    concept_name: str
    concept_code: str
    domain_id: str | None
    concept_class_id: str | None
    vocabulary_id: str | None
    standard_concept: str | None

@dataclass(frozen=True)
class LookupIndex:
    name: str
    unknown: int | None
    mapping: dict[str, int]

    def lookup(self, term: str | None) -> int | None:
        if term is None:
            term = ""
        return self.mapping.get(term, self.unknown)

    def __contains__(self, item: str | int) -> bool:
        if isinstance(item, str):
            return item in self.mapping
        if isinstance(item, int):
            return item in self.mapping.values()
        return False

    @property
    def all_concepts(self) -> set[int]:
        return set(self.mapping.values())
    
Normaliser = Callable[[str], str]

@dataclass(frozen=True)
class LookupSpec:
    name: str
    unknown: int | None = 0
    domain_id: str | None = None
    concept_class_id: list[str] | None = None
    vocabulary_id: list[str] | None = None
    standard_only: bool = True
    code_filter: str | None = None
    parents: list[int] | None = None
    include_non_standard_descendants: bool = False
    include_synonyms: bool = False
    normalizer: Normaliser = normalize_default
    include: tuple[str, ...] = ("concept_name", "concept_code")  # index fields

@dataclass(frozen=True)
class MappingRow:
    table: str
    column: str
    context: str | None
    value: str
    concept_id: int

class MappingSource(Protocol):
    def fetch_mappings(self, *, table: str, columns: list[str]) -> list[MappingRow]:
        ...

@dataclass(frozen=True)
class MappingSpec:
    name: str
    table: str
    columns: list[str]
    unknown: int | None
    context_default: str = "all"
    normalizer: Normaliser = normalize_default