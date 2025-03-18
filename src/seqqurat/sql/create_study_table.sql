CREATE OR REPLACE TABLE  study_index (
    dateAddedToCatalog DATE,
    pubmedId UINTEGER,
    firstAuthor VARCHAR,
    publicationDate DATE,
    publicationJournal VARCHAR,
    publicationLink VARCHAR,
    publicationName VARCHAR,
    phenotype VARCHAR,
    initialSampleSize VARCHAR,
    replicationSampleSize VARCHAR,
    platform VARCHAR,
    associationCount UINTEGER,
    mappedTrait VARCHAR,
    mappedTraitURI VARCHAR,
    studyAccession VARCHAR,
    genotypingTechnology VARCHAR,
    submissionDate DATE,
    statisticalModel VARCHAR,
    backgroundTrait VARCHAR,
    mappedBackgroundTrait VARCHAR,
    mappedBackgroundTraitURI VARCHAR,
    cohort VARCHAR,
    fullSummaryStatistics BOOLEAN,
    summaryStatisticsLocation VARCHAR,
    gxe BOOLEAN,
);

BEGIN TRANSACTION;
COPY study_index 
FROM 'tests/data/gwas-catalog-v1.0.3.1-studies-r2025-03-08.tsv' 
    (DELIMITER '\t', HEADER false, SKIP 1);

COMMIT;
DESCRIBE study_index;

