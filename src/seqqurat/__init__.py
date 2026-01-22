"""Seqqurat library."""

import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from returns.result import Success

from seqqurat.extractor import GWASCatalogStudyStore
from seqqurat.open_targets import OpenTargetsDatasetSchemaRegistry
from seqqurat.query_parser import QueryResolver, SeqquratQueryName


class View(StrEnum):
    """Enum for different queries."""

    THERAPEUTIC_AREAS = 'therapeutic_areas'
    COLOCALISATION_STATS = 'colocalisation_stats'
    TRANS_ENHANCERS = 'trans_enhancers'
    OTHER = 'other'
    VARIANT_MAF = 'variant_maf'


DB_FILE = Path('gwas.db')
OT_DB_FILE = Path('ot.db')

cli = typer.Typer(no_args_is_help=True)


def db_callback(value: Path):
    """Callback to validate the database existence."""
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
        typer.Argument(help='Path to the parquet output db file', callback=db_callback),
    ] = OT_DB_FILE,
    release: Annotated[str, typer.Option(help='OpenTargets release version to validate against.')] | None = None,
    view: Annotated[list[View] | None, typer.Option(help='Views to include in the database.')] = None,
    dry_run: Annotated[bool, typer.Option(help='If set, will not build the database.')] = False,
):
    """Build OpenTargets duckdb database."""
    logger.info('Extracting information from output dataset.')
    if view:
        logger.info(f'Including views: {view}')
    if dry_run:
        logger.info('Dry run set, exiting now.')
        sys.exit(0)
    schema_registry = OpenTargetsDatasetSchemaRegistry(directory=output_datasets_path)
    model = schema_registry.validate(release=release)
    match model:
        case Success(_model):
            db = GWASCatalogStudyStore.build(location=db_path)
            logger.info(f'Using validated model for release: {_model.release}')
            _directories = _model.datasets
            for d in _directories:
                env = {'output_dataset_path': str(d) + '/*.parquet', 'table_name': d.stem}
                logger.info(f'Using {env} to build {env["output_dataset_path"]}')
                try:
                    statements = QueryResolver(env=env).get(SeqquratQueryName.CREATE_OT_TABLE).unwrap()
                    db.execute(statements)
                except Exception as e:
                    logger.warning(f'Failed to create table for {d.stem} with error: {e}')
                    logger.info('Attempting hive partitioned table creation')
                    env['output_dataset_path'] = str(d) + '/*/*.parquet'
                    statements = QueryResolver(env=env).get(SeqquratQueryName.CREATE_OT_HIVE_TABLE).unwrap()
                    db.execute(statements)
            if view:
                for v in view:
                    match v:
                        case View.THERAPEUTIC_AREAS:
                            logger.info('Adding therapeutic areas view.')
                            statements = QueryResolver().get(SeqquratQueryName.THERAPEUTIC_AREAS).unwrap()
                            db.execute(statements)
                        case View.COLOCALISATION_STATS:
                            logger.info('Adding colocalisation stats views.')
                            statements = QueryResolver().get(SeqquratQueryName.COLOCALISATION_STATS).unwrap()
                        case View.TRANS_ENHANCERS:
                            logger.info('Adding trans enhancer effects view.')
                            statements = QueryResolver().get(SeqquratQueryName.TRANS_ENHANCERS).unwrap()
                            db.execute(statements)
                        case View.VARIANT_MAF:
                            logger.info('Adding variant MAF view.')
                            statements = QueryResolver().get(SeqquratQueryName.VARIANT_MAF).unwrap()
                            db.execute(statements)
                        case _:
                            logger.warning(f'View {v} not recognised, skipping.')

        case _:
            logger.debug('No valid OpenTargets dataset structure found.')
            sys.exit(1)
