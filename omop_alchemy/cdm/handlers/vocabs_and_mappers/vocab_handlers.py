from typing import Protocol, Iterable, Optional
from dataclasses import dataclass
from typing import Callable
from collections import defaultdict
import sqlalchemy as sa
import sqlalchemy.orm as so
from .typing import ConceptRow, LookupIndex, LookupSpec, Normaliser
from .vocab_helpers import normalize_default, compose_normalizers
from ...model.vocabulary import Concept, Concept_Synonym, Concept_Relationship, Concept_Ancestor


# this is somewhat redunant with some of omop-graph but 
# mutual dependency is awkward and this is a very thin layer so 
# it's not worth over-engineering the separation at this stage

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

    @staticmethod
    def fetch_synonyms(session: so.Session) -> list[tuple[int, str]]:
        """
        Return (concept_id, synonym) pairs for all concept synonyms.

        Filtering (standard / domain / etc.) is intentionally left
        to higher layers.
        """
        rows = session.execute(
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
    
    @staticmethod
    def fetch_concepts(
        session: so.Session,
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

        q = session.query(Concept)
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
    
    @staticmethod
    def descendants(
        session: so.Session,
        parents: list[int],
        *,
        include_non_standard: bool = False,
    ) -> list[int]:
        rows = OMOPConceptSource.fetch_concepts(
            session,
            parents=parents,
            include_non_standard_descendants=include_non_standard,
            standard_only=not include_non_standard,
        )
        return list({r.concept_id for r in rows})
    
class LookupBuilder:
    def build(self, session: so.Session, spec: LookupSpec) -> LookupIndex:
        rows = OMOPConceptSource.fetch_concepts(
            session,
            domain_id=spec.domain_id,
            concept_class_id=spec.concept_class_id,
            vocabulary_id=spec.vocabulary_id,
            standard_only=spec.standard_only,
            code_filter=spec.code_filter,
            parents=spec.parents,
            include_non_standard_descendants=spec.include_non_standard_descendants,
        )

        ids = {r.concept_id for r in rows}

        m: dict[str, int] = {}
        for r in rows:
            if "concept_name" in spec.include and r.concept_name:
                m[spec.normalizer(r.concept_name)] = r.concept_id
            if "concept_code" in spec.include and r.concept_code:
                m[spec.normalizer(r.concept_code)] = r.concept_id

        if spec.include_synonyms:
            for cid, syn in OMOPConceptSource.fetch_synonyms(session):
                if cid in ids and syn:
                    m[spec.normalizer(syn)] = cid

        return LookupIndex(name=spec.name, unknown=spec.unknown, mapping=m)


class ConceptResolver:
    def __init__(
        self,
        index: LookupIndex,
        *,
        normalizer: Normaliser | None = None,
        corrections: list[Callable[[str], str]] | None = None,
    ):
        self.index = index
        self._normalizer = normalizer or normalize_default
        self._corrections = corrections or []

    def lookup(self, term: str | None) -> int | None:
        if not term:
            return self.index.unknown

        key = self._normalizer(term)
        hit = self.index.mapping.get(key)
        if hit is not None:
            return hit

        for corr in self._corrections:
            key2 = self._normalizer(corr(term))
            hit = self.index.mapping.get(key2)
            if hit is not None:
                return hit

        return self.index.unknown

    def lookup_exact(self, term: str | None) -> int | None:
        if not term:
            return self.index.unknown
        return self.index.mapping.get(self._normalizer(term), self.index.unknown)

    def __contains__(self, item: str | int) -> bool:
        if isinstance(item, int):
            return item in self.index.mapping.values()
        if isinstance(item, str):
            return self.lookup(item) != self.index.unknown
        return False

    @property
    def all_concepts(self) -> set[int]:
        return set(self.index.mapping.values())
