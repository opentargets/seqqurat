"""Seqqurat library."""

from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from seqqurat.extractor import GWASCatalogStudyStore
from seqqurat.query_parser import QueryResolver, SeqquratQueryName

DB_FILE = Path('gwas.db')

cli = typer.Typer(no_args_is_help=True)


def parquet_callback(value: Path):
    """Callback to validate the parquet requirement flag."""
    print(value.is_file())
    if value.suffix != '.parquet':
        raise typer.BadParameter('Must be path to the parquet file.')
    if value.exists():
        raise typer.BadParameter(f'Path to {value} exists.')
    return value


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
    db.execute(statements)


@cli.command()
def extract_seqwas(
    output_path: Annotated[
        Path,
        typer.Option(help='Path to the parquet output file.', callback=parquet_callback),
    ],
    db_path: Annotated[Path, typer.Argument(help='Path where the study metadata will be stored.')] = DB_FILE,
):
    """Extract Exome sequencing GWAS from db."""
    logger.info('Extracting seqwas data from study_index table.')
    env = {'seqwas_studies': str(output_path)}
    statements = QueryResolver(env=env).get(SeqquratQueryName.EXTRACT_SEQWAS).unwrap()
    db = GWASCatalogStudyStore.build(location=db_path)
    db.execute(statements)
