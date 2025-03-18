"""Seqqurat library."""

from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from seqqurat.extractor import GWASCatalogStudyStore
from seqqurat.query_parser import QueryResolver, SeqquratQueryName

DB_FILE = Path('gwas.db')

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def study_index(
    study_file: Annotated[
        Path, typer.Argument(help='Path to the original data to use to build the study metadata database.')
    ],
    db_path: Annotated[Path, typer.Argument(help='Path where the study metadata will be stored.')] = DB_FILE,
):
    """Build a database for GWAS Catalog metadata."""
    logger.info(f'Building database at {db_path}')
    logger.info(
        f'Using study file from {study_file}',
    )
    qr = QueryResolver(env={'study_file': str(study_file)})
    statements = qr.get(SeqquratQueryName.CREATE_STUDY_TABLE).unwrap()
    db = GWASCatalogStudyStore.build(location=db_path)
    logger.info('Executing')
    db.execute(statements)


@cli.command()
def extract_seqwas(db_path: Annotated[Path, typer.Argument]):
    """Extract Exome sequencing GWAS from db."""
    logger.info(f'Building database at {db_path}')
