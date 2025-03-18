-- Build the study_index table from GWAS Catalog study index.
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
FROM '{study_file}'
    (DELIMITER '\t', HEADER false, SKIP 1);

COMMIT;
DESCRIBE study_index;

