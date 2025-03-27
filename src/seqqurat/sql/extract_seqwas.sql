-- Extract Sequencing based GWAS studies available in study_index table.

BEGIN TRANSACTION;
CREATE OR REPLACE VIEW seqwas_study_index  AS 
SELECT * 
FROM 
    study_index 
WHERE genotypingTechnology NOT ILIKE '%array%' AND fullSummaryStatistics;
COMMIT;

SELECT * FROM seqwas_study_index;
COPY seqwas_study_index TO '{seqwas_studies}' (FORMAT parquet);
