"""Query parser for duckdb SQL queries written in script."""

from __future__ import annotations

from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

from duckdb import ParserException, Statement, extract_statements
from loguru import logger
from returns.result import Failure, Result, Success

from seqqurat.errors import SeqquratError

if TYPE_CHECKING:
    from collections.abc import Sequence


def read_sql_statements(file: Path, env: dict[str, str]) -> Result[Sequence[Statement], SeqquratError]:
    """Read sql statement and map the environment variables to the templates.

    :param file: Path to the template.
    :type file: Path
    :param env: Environment variables to process the template query.
    :type env: dict[str, str]
    :return: Enum of either duckdb statement sequence of error.
    :rtype: Result[Sequence[Statement], SeqquratError]
    """
    with open(file) as f:
        queries = f.read()
        logger.debug(f'Replacing {env}')
        for k, v in env.items():
            key_replacement = '{%s}' % k  # noqa: UP031
            queries = queries.replace(key_replacement, v)
    try:
        statements = extract_statements(query=queries)
        return Success(statements)

    except ParserException as e:
        logger.error(e)
        return Failure(SeqquratError.QUERY_FILE_PARSING_ERROR)


class QueryResolver:
    """Object used to get the queries defined in the seqqurat package metadata."""

    def __init__(self, env: dict[str, str] | None = None) -> None:
        """Class to store all queries defined in the project.

        :param env: Environment variables to process the template query.
        :type env: dict[str, str] | None
        """
        query_files = (Path(str(f)) for f in files('seqqurat.sql').iterdir())
        query_files = (p for p in query_files if p.is_file() and p.suffix == '.sql')
        # can call unwrap with no error, since all queries defined in the package should be parsable!
        env = env or {}
        self.queries = {p.name.removesuffix('.sql'): read_sql_statements(p, env).unwrap() for p in query_files}

    def get(self, query_name: SeqquratQueryName) -> Result[Sequence[Statement], SeqquratError]:
        """Get the statements for the sql query."""
        statements = self.queries.get(query_name)
        if not statements:
            return Failure(SeqquratError.QUERY_NOT_FOUND)
        return Success(statements)


class SeqquratQueryName(StrEnum):
    """In-house query names defined for the seqqurat package."""

    CREATE_STUDY_TABLE = 'create_study_table'
    EXTRACT_SEQWAS = 'extract_seqwas'
