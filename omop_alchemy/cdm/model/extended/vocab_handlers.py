from typing import Protocol, Iterable, Optional
from dataclasses import dataclass
from typing import Callable
from collections import defaultdict
import sqlalchemy as sa
import sqlalchemy.orm as so
from ..vocabulary import Concept, Concept_Synonym, Concept_Relationship, Concept_Ancestor


@dataclass(frozen=True)
class ConceptRow:
    concept_id: int
    concept_name: str
    concept_code: str
    domain_id: str | None
    concept_class_id: str | None
    vocabulary_id: str | None
    standard_concept: str | None

class ConceptSource(Protocol):

    def fetch_concepts(
        self,
        *,
        domain_id: str | None = None,
        concept_class_id: Iterable[str] | None = None,
        vocabulary_id: Iterable[str] | None = None,
        standard_only: bool = True,
        code_filter: str | None = None,
        parents: Iterable[int] | None = None,
        include_non_standard_descendants: bool = False,
    ) -> list[ConceptRow]:
        ...


class OMOPConceptSource:
    """
    Concrete ConceptSource backed by OMOP CDM vocabulary tables.

    This class:
    - performs NO caching
    - performs NO normalisation
    - performs NO lookup logic

    It is a thin, explicit adapter between SQLAlchemy + OMOP CDM
    and higher-level vocabulary indexing logic.
    """
    def __init__(self, session: so.Session):
        if session.bind is None:
            raise RuntimeError("Session is not bound to an engine")
        self.session = session

    def fetch_synonyms(self) -> list[tuple[int, str]]:
        """
        Return (concept_id, synonym) pairs for all concept synonyms.

        Filtering (standard / domain / etc.) is intentionally left
        to higher layers.
        """
        rows = self.session.execute(
            sa.select(
                Concept_Synonym.concept_id,
                Concept_Synonym.concept_synonym_name,
            )
        ).all()

        return [
            (int(r.concept_id), r.concept_synonym_name)
            for r in rows
            if r.concept_synonym_name
        ]
    

    def fetch_concepts(
        self,
        *,
        domain_id: str | None = None,
        concept_class_id: Iterable[str] | None = None,
        vocabulary_id: Iterable[str] | None = None,
        standard_only: bool = True,
        code_filter: str | None = None,
        parents: Iterable[int] | None = None,
        include_non_standard_descendants: bool = False,
    ) -> list[ConceptRow]:
        """
        Fetch concepts matching the provided constraints.

        This method supports two primary modes:
        1. Flat filtering by domain / class / vocabulary
        2. Hierarchical expansion from parent concept(s)

        The semantics are explicit and intentionally conservative.
        """

        q = self.session.query(Concept)
        if parents:
            parents = list(parents)
            q = (
                q.join(
                    Concept_Ancestor,
                    Concept_Ancestor.descendant_concept_id == Concept.concept_id,
                )
                .filter(
                    Concept_Ancestor.ancestor_concept_id.in_(parents)
                )
            )

            if standard_only and not include_non_standard_descendants:
                q = q.filter(Concept.standard_concept == "S")
            
        if domain_id:
            q = q.filter(Concept.domain_id == domain_id)

        if concept_class_id:
            q = q.filter(
                Concept.concept_class_id.in_(list(concept_class_id))
            )

        if vocabulary_id:
            q = q.filter(
                Concept.vocabulary_id.in_(list(vocabulary_id))
            )
        if standard_only and not parents:
            q = q.filter(Concept.standard_concept == "S")

        if code_filter:
            q = q.filter(
                Concept.concept_code.ilike(f"%{code_filter}%")
            )
        rows = q.all()
        return [
            ConceptRow(
                concept_id=int(r.concept_id),
                concept_name=r.concept_name,
                concept_code=r.concept_code,
                domain_id=r.domain_id,
                concept_class_id=r.concept_class_id,
                vocabulary_id=r.vocabulary_id,
                standard_concept=r.standard_concept,
            )
            for r in rows
        ]
    
Normaliser = Callable[[str], str]

def normalize_default(s: str) -> str:
    return s.strip().lower()

def compose_normalizers(*fns: Normaliser) -> Normaliser:
    def _inner(s: str) -> str:
        for fn in fns:
            s = fn(s)
        return s
    return _inner


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

class LookupBuilder:
    def __init__(self, source: ConceptSource):
        self.source = source

    def build(self, spec: LookupSpec) -> LookupIndex:
        rows = self.source.fetch_concepts(
            domain_id=spec.domain_id,
            concept_class_id=spec.concept_class_id,
            vocabulary_id=spec.vocabulary_id,
            standard_only=spec.standard_only,
            code_filter=spec.code_filter,
            parents=spec.parents,
            include_non_standard_descendants=spec.include_non_standard_descendants,
        )

        m: dict[str, int] = {}
        for r in rows:
            if "concept_name" in spec.include:
                m[spec.normalizer(r.concept_name)] = r.concept_id
            if "concept_code" in spec.include:
                m[spec.normalizer(r.concept_code)] = r.concept_id

        
        if spec.include_synonyms:
            for cid, syn in self.source.fetch_synonyms():
                m[spec.normalizer(syn)] = cid

        return LookupIndex(name=spec.name, unknown=spec.unknown, mapping=m)
    


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


LOOKUP_SPECS = {
    "gender": LookupSpec(name="gender", domain_id="Gender", standard_only=True, unknown=0),
    "unit": LookupSpec(name="unit", domain_id="Unit", standard_only=True, unknown=0),
    "grading": LookupSpec(
        name="grading",
        domain_id="Measurement",
        concept_class_id=["Staging/Grading"],
        code_filter="grade",
        standard_only=True,
        unknown=0,
    ),
    # etc
}

def build_lookups(session: so.Session) -> dict[str, LookupIndex]:
    source = OMOPConceptSource(session)
    builder = LookupBuilder(source)
    return {k: builder.build(spec) for k, spec in LOOKUP_SPECS.items()}


class HierarchyService:
    def __init__(self, source: ConceptSource):
        self.source = source

    def descendants(self, parents: list[int]) -> list[int]:
        ...