"""Seqqurat library."""

from pathlib import Path
from typing import Annotated

import typer
from duckdb import IOException
from loguru import logger
from returns.result import Success

from seqqurat.extractor import GWASCatalogStudyStore
from seqqurat.open_targets import OpenTargetOutputDataset, SubdirectoryValidator
from seqqurat.query_parser import QueryResolver, SeqquratQueryName

DB_FILE = Path('gwas.db')

cli = typer.Typer(no_args_is_help=True)


def db_callback(value: Path):
    """Callback to validate the database existance."""
    return value


def parquet_callback(value: Path):
    """Callback to validate the parquet requirement flag."""
    if value.suffix != '.parquet':
        raise typer.BadParameter('Must be path to the parquet file.')
    if value.exists():
        raise typer.BadParameter(f'Path to {value} exists.')
    return value


def output_datasets_path(value: Path):
    """Callback to validate the output datasets path."""
    if not value.exists():
        raise typer.BadParameter('Path to output_datasets must exist.')
    if not value.is_dir():
        raise typer.BadParameter('Path to output_datasets must be a directory')
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


@cli.command()
def build_ot_db(
    output_datasets_path: Annotated[
        Path,
        typer.Option(help='Path to the OpenTargets output datasets', callback=output_datasets_path),
    ],
    db_path: Annotated[
        Path,
        typer.Option(help='Path to the parquet output db file', callback=db_callback),
    ] = DB_FILE,
):
    """Build OpenTargets duckdb database."""
    logger.info('Extracting information from output dataset.')
    all_possible_paths = {output_datasets_path / ds.value for ds in OpenTargetOutputDataset}
    directories = SubdirectoryValidator(output_datasets_path).validate(all_possible_paths)
    match directories:
        case Success(_directories):
            db = GWASCatalogStudyStore.build(location=db_path)
            for d in _directories:
                env = {'output_dataset_path': str(d) + '/*.parquet', 'table_name': d.stem}
                logger.info(f'Using {env} to build {env["output_dataset_path"]}')
                if d.stem == 'evidence':
                    logger.error(env)
                    env['output_dataset_path'] = str(d) + '/*/*.parquet'
                    statements = QueryResolver(env=env).get(SeqquratQueryName.CREATE_OT_HIVE_TABLE).unwrap()
                else:
                    statements = QueryResolver(env=env).get(SeqquratQueryName.CREATE_OT_TABLE).unwrap()
                db.execute(statements)
