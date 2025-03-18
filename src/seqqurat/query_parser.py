"""Query parser for duckdb SQL queries written in script."""

from __future__ import annotations

from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

from duckdb import ParserException, Statement, extract_statements
from returns.result import Failure, Result, Success

from seqqurat.errors import SeqquratError

if TYPE_CHECKING:
    from collections.abc import Sequence


def read_sql_statements(file: Path) -> Result[Sequence[Statement], SeqquratError]:
    """Read sql statements from file."""
    with open(file) as f:
        queries = f.read()
    try:
        return Success(extract_statements(query=queries))

    except ParserException:
        return Failure(SeqquratError.QUERY_FILE_PARSING_ERROR)


class QueryResolver:
    """Object used to get the queries defined in the seqqurat package metadata."""

    def __init__(self) -> None:
        """Class to store all queries defined in the project."""
        query_files = (Path(str(f)) for f in files('seqqurat.sql').iterdir())
        query_files = (p for p in query_files if p.is_file() and p.suffix == '.sql')
        # can call unwrap with no error, since all queries defined in the package should be parsable!
        self.queries = {p.name.removesuffix('.sql'): read_sql_statements(p).unwrap() for p in query_files}

    def get(self, query_name: SeqquratQueryName) -> Result[Sequence[Statement], SeqquratError]:
        """Get the statements for the sql query."""
        statements = self.queries.get(query_name)
        if not statements:
            return Failure(SeqquratError.QUERY_NOT_FOUND)
        return Success(statements)


class SeqquratQueryName(StrEnum):
    """In-house query names defined for the seqqurat package."""

    CREATE_STUDY_TABLE = 'create_study_table'
