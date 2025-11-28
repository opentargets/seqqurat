BEGIN TRANSACTION;

/*
 Therapeutic areas table
 */
CREATE
OR REPLACE TABLE therapeutic_areas AS (
    (
        SELECT
            disease.id AS therapeuticAreaId,
            disease.name AS therapeuticAreaName,
        FROM
            disease
        WHERE
            length(disease.parents) = 0
    )
);

/*
 View to link therapeutic areas to diseases
 */
CREATE
OR REPLACE VIEW therapeutic_areas_lut AS (
    SELECT
        therapeuticAreaId,
        therapeuticAreaName,
        diseaseId,
        diseaseName
    FROM
        (
            SELECT
                disease.id AS diseaseId,
                disease.name AS diseaseName,
                unnest(disease.therapeuticAreas) AS therapeuticAreaId
            FROM
                disease
        )
        JOIN (
            SELECT
                therapeuticAreaId,
                therapeuticAreaName
            FROM
                therapeutic_areas
        ) USING (therapeuticAreaId)
);

/* 
 * View to link studies to therapeutic areas
 */
CREATE VIEW study_per_therapeutic_area AS (
    WITH si AS (
        SELECT
            study.studyId AS studyId,
            unnest(study.diseaseids) AS diseaseid
        FROM
            study
    )
    SELECT
        si.studyId,
        tal.therapeuticAreaId,
        tal.therapeuticAreaName
    FROM
        si
        JOIN therapeutic_areas_lut tal USING (diseaseid)
);

/*
 * View to link credible sets to therapeutic areas
 */
CREATE
OR REPLACE VIEW credible_sets_per_therapeutic_area AS (
    WITH cs AS (
        SELECT
            credible_set.studyId AS studyId,
            credible_set.studyLocusId AS credibleSetId,
        FROM
            credible_set
    )
    SELECT
        cs.credibleSetId,
        tal.therapeuticAreaId,
        tal.therapeuticAreaName
    FROM
        cs
        JOIN study_per_therapeutic_area tal USING (studyId)
);

END TRANSACTION;