"""Implementation of OpenTargets output directory validator."""

from __future__ import annotations

from pathlib import Path

import loguru
import yaml
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from seqqurat.errors import SeqquratError


class OpenTargetsDatasetModel(BaseModel):
    """OpenTargets dataset representation."""

    release: str
    datasets: list[Path]

    @classmethod
    def from_path(cls, p: Path) -> OpenTargetsDatasetModel:
        """Create OpenTargetsDatasetModel from path."""
        try:
            with p.open('r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            loguru.logger.error(f'Error loading YAML file at {p}: {e}')
            raise
        return cls(**data)


class OpenTargetsDatasetSchemaRegistry:
    """OpenTargets datasets."""

    BASE_SCHEMA_PATH = Path(__file__).parent / 'assets' / 'release_schemas'

    SCHEMA_PATHS = {
        '25.03': BASE_SCHEMA_PATH / '25.03' / 'release.yaml',
        '25.06': BASE_SCHEMA_PATH / '25.06' / 'release.yaml',
        '25.09': BASE_SCHEMA_PATH / '25.09' / 'release.yaml',
        '25.12': BASE_SCHEMA_PATH / '25.12' / 'release.yaml',
        '25.12-ppp': BASE_SCHEMA_PATH / '25.12-ppp' / 'release.yaml',
    }

    SCHEMA = {r: OpenTargetsDatasetModel.from_path(p) for r, p in SCHEMA_PATHS.items()}

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def validate(self, release: str | None = None) -> Result[OpenTargetsDatasetModel, SeqquratError]:
        """Validate if the subdirectories exist in the parent dir.

        The logic behind validation is as follows:
        (1) if a release is provided, validate against that release schema only.
            If validation fails, return an error.
        (2) if no release is provided, iterate over all known release schemas
            and validate against each one until a match is found. If no match is found,
            return an error.
        """
        if release:
            loguru.logger.info(f'Validating against specified release schema: {release}')
            model = self.SCHEMA.get(release)
            if not model:
                loguru.logger.error(f'No schema found for release: {release}')
                return Failure(SeqquratError.MISSING_RELEASE_SCHEMA)
            _expected_dirs = {self.directory / d for d in model.datasets}
            _asserted_paths = set(self.directory.iterdir())
            if not _expected_dirs.issubset(_asserted_paths):
                loguru.logger.error(f'Validation failed for release: {release}')
                missing = _expected_dirs - _asserted_paths
                loguru.logger.error(f'Missing directories: {missing}')
                return Failure(SeqquratError.OUTPUT_DIR_VALIDATION_ERROR)
            return Success(OpenTargetsDatasetModel(release=release, datasets=list(_expected_dirs)))

        found_model = None
        for r, model in self.SCHEMA.items():
            loguru.logger.info(f'Validating against release schema: {r}')
            _expected_dirs = {self.directory / d for d in model.datasets}
            _asserted_paths = set(self.directory.iterdir())
            if not _expected_dirs.issubset(_asserted_paths):
                loguru.logger.info(f'Validation failed for release: {r}')
                missing = _expected_dirs - _asserted_paths
                loguru.logger.info(f'Missing directories: {missing}')
                continue
            found_model = model
            found_model = OpenTargetsDatasetModel(release=r, datasets=list(_expected_dirs))
            loguru.logger.info(f'Validation succeeded for release: {r}')
            break
        if not found_model:
            return Failure(SeqquratError.MISSING_RELEASE_SCHEMA)
        return Success(found_model)
