"""Extractor class for seq-was."""

from __future__ import annotations

from pathlib import Path

import duckdb as duck
from loguru import logger

from seqqurat.store import Store


class GWASCatalogStudyStore(Store):
    """GWAS Catalog study metastore."""

    @classmethod
    def build(cls, location: Path) -> Store:
        """Build the database."""
        db = cls(location)
        if not location.exists():
            logger.info('GWAS Catalog extractor database not detected, building')
            duck.connect(database=location).close()
        else:
            logger.info('GWAS Catalog extractor database detected')
        return db
