"""Implementation of OpenTargets output directory validator."""

from enum import StrEnum
from pathlib import Path

from returns.result import Failure, Result, Success

from seqqurat.errors import SeqquratError


class OpenTargetOutputDataset(StrEnum):
    """Representation of directory names used at open targets output datasets."""

    ASSOCIATION_BY_DATASOURCE_DIRECT = 'association_by_datasource_direct'
    ASSOCIATION_BY_DATASOURCE_INDIRECT = 'association_by_datasource_indirect'
    ASSOCIATION_BY_DATATYPE_DIRECT = 'association_by_datatype_direct'
    ASSOCIATION_BY_DATATYPE_INDIRECT = 'association_by_datatype_indirect'
    ASSOCIATION_BY_OVERALL_INDIRECT = 'association_by_overall_indirect'
    ASSOCIATION_OVERALL_DIRECT = 'association_overall_direct'
    BIOSAMPLE = 'biosample'
    COLOCALISATION_COLOC = 'colocalisation_coloc'
    COLOCALISATION_ECAVIAR = 'colocalisation_ecaviar'
    CREDIBLE_SET = 'credible_set'
    DISEASE = 'disease'
    DISEASE_HPO = 'disease_hpo'
    DISEASE_PHENOTYPE = 'disease_phenotype'
    DRUG_INDICATION = 'drug_indication'
    DRUG_MECHANISM_OF_ACTION = 'drug_mechanism_of_action'
    DRUG_MOLECULE = 'drug_molecule'
    DRUG_WARNING = 'drug_warning'
    EVIDENCE = 'evidence'
    EXPRESSION = 'expression'
    GO = 'go'
    INTERACTION = 'interaction'
    INTERACTION_EVIDENCE = 'interaction_evidence'
    KNOWN_DRUG = 'known_drug'
    L2G_PREDICTION = 'l2g_prediction'
    LITERATURE = 'literature'
    LITERATURE_VECTOR = 'literature_vector'
    MOUSE_PHENOTYPE = 'mouse_phenotype'
    OPENFDA_SIGNIFICANT_ADVERSE_DRUG_REACTIONS = 'openfda_significant_adverse_drug_reactions'
    OPENFDA_SIGNIFICANT_ADVERSE_TARGET_REACTIONS = 'openfda_significant_adverse_target_reactions'
    PHARMACOGENOMICS = 'pharmacogenomics'
    REACTOME = 'reactome'
    SO = 'so'
    STUDY = 'study'
    TARGET = 'target'
    TARGET_ESSENTIALITY = 'target_essentiality'
    TARGET_PRIORITISATION = 'target_prioritisation'
    VARIANT = 'variant'


class SubdirectoryValidator:
    """Subdirectory validator."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def validate(self, expected_dirs: set[Path]) -> Result[set[Path], SeqquratError]:
        """Validate if the subdirectories exist in the parent dir."""
        _expected_dirs = set(expected_dirs)
        _asserted_paths = set(self.directory.iterdir())
        if not _expected_dirs.issubset(_asserted_paths):
            return Failure(SeqquratError.OUTPUT_DIR_VALIDATION_ERROR)
        return Success(_expected_dirs)
