"""Store implementation based on duckdb python API client."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import duckdb as duck
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Sequence


class Store:
    """Generic class representing the duckdb database."""

    def __init__(self, location: Path):
        self.location = location

    @property
    def created(self) -> bool:
        """Wether the database was created."""
        return False

    @property
    def connected(self) -> bool:
        """Wether the connection to the database was done."""
        return False

    def execute(self, query: str | Sequence[str] | duck.Statement | Sequence[duck.Statement]):
        """Execute queries or statements."""
        with duck.connect(self.location) as conn:
            # print(query)
            match query:
                case list():
                    for q in query:
                        if isinstance(q, duck.Statement):
                            q = q.query
                        logger.info(f'Executing query {q}')
                        df = duck.sql(q, connection=conn)
                        print(df)  # noqa: T201
                case _:
                    logger.info('Executing one query')
                    duck.execute(query, connection=conn)

    @classmethod
    def build(cls, location: Path) -> Store:
        """Build the database in the provided location."""
        raise NotImplementedError('implement in child classes')
