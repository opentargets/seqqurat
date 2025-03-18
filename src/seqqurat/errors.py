"""Module containing errors for seqqurat package."""

from enum import StrEnum


class SeqquratError(StrEnum):
    """Errors produced by Seqqurat package."""

    QUERY_NOT_FOUND = 'Provided query was not found.'
    QUERY_FILE_PARSING_ERROR = 'duckdb was not able to parse provided query file.'
    QUERY_FAILED = 'duckdb was not able to run the query.'
