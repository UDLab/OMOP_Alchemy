
from __future__ import annotations
import sqlalchemy.orm as so
import sqlalchemy as sa
from typing import Type, Any
from sqlalchemy.ext.declarative import declared_attr

class ReferenceContext:

    """
    `ReferenceContext` 
    
    A helper base class for defining **read-only reference relationships**.

    This class is purely structural: it resolves foreign keys
    into reference tables (Domain, Vocabulary, ConceptClass, etc.)
    with explicit join conditions.

    
    These relationships are:

    - `viewonly=True`
    - explicitly joined
    - resolved lazily using `selectin`
    - defined outside the core table

    They are intended for:

    - inspection
    - analytics
    - debugging
    - view-level navigation
    — **not** for ETL or mutation.
    """

    @classmethod
    def _reference_relationship(
        cls,
        *,
        target: str,
        local_fk: str,
        remote_pk: str,
        uselist: bool = False,
    ):
        return so.declared_attr(
            lambda cls_: so.relationship(
                target,
                primaryjoin=lambda: getattr(cls_, local_fk) == getattr(
                    sa.inspect(cls_).registry._class_registry[target],
                    remote_pk,
                ),
                foreign_keys=lambda: getattr(cls_, local_fk),
                viewonly=True,
                lazy="selectin",
                uselist=uselist,
            )
        )