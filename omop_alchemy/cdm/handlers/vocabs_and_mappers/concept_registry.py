from collections.abc import Mapping
from typing import Callable
import sqlalchemy as sa
import sqlalchemy.orm as so

from .vocab_handlers import ConceptResolver

class ConceptResolverRegistry:
    """
    Lazy registry for ConceptResolvers.

    Resolvers are constructed on first access and cached for the lifetime
    of this registry instance. The registry is scoped to a SQLAlchemy Engine,
    ensuring vocab lookups are built once per database.
    """

    def __init__(self, engine: sa.Engine):
        self.engine = engine
        self._cache: dict[str, ConceptResolver] = {}

    def get(self, name: str, builder: Callable[[so.Session], ConceptResolver]) -> ConceptResolver:
        """
        Return a cached resolver by name, building it if required.

        Parameters
        ----------
        name:
            Stable key identifying this resolver (e.g. "tnm_t_stage").
        builder:
            Callable that constructs the resolver given a Session.
            This is only invoked on first access.
        """
        if name in self._cache:
            return self._cache[name]

        with so.Session(self.engine) as session:
            resolver = builder(session)

        self._cache[name] = resolver
        return resolver
