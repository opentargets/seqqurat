BEGIN TRANSACTION;

/**
 * View to filter colocalisation results for meaningful colocs
 * This view selects colocs with h4 >= 0.8 or clpp >= 0.01
 */
CREATE VIEW meaningful_colocs AS
SELECT
    leftStudyLocusId,
    rightStudyType
FROM
    colocalisation
WHERE
    (
        (h4 >= 0.8)
        OR (clpp >= 0.01)
    );

COMMIT;

BEGIN TRANSACTION;

/**
 * View of GWAS credible sets
 */
CREATE VIEW gwas_cs AS
SELECT
    *
FROM
    credible_set
WHERE
    (studyType = 'gwas');

COMMIT;

BEGIN TRANSACTION;

/**
 * View of GWAS loci that colocalise with meaningful colocs
 */
CREATE VIEW gwas_cs_colocalised AS
SELECT
    leftStudyLocusId,
    rightStudyType
FROM
    (
        SELECT
            A.leftStudyLocusId,
            B.rightStudyType
        FROM
            (
                SELECT
                    studyLocusId AS leftStudyLocusId
                FROM
                    gwas_cs
            ) AS A
            LEFT JOIN (
                SELECT
                    leftStudyLocusId,
                    rightStudyType
                FROM
                    meaningful_colocs
            ) AS B ON ((A.leftStudyLocusId = B.leftStudyLocusId))
    );

COMMIT;

BEGIN TRANSACTION;

/**
 * View to summarise colocalisation statistics
 * This is the total number of colocalised GWAS credible sets per combination of colocalised study types
 */
CREATE VIEW colocalisation_stats AS
SELECT
    colocalisedStudyTypes,
    cnt,
    (
        round(((cnt / sum(cnt) OVER ()) * 100), 2) || '%'
    ) AS pct,
    round(((cnt / sum(cnt) OVER ()) * 100), 2) AS percentage
FROM
    (
        SELECT
            isColocalisedVec AS colocalisedStudyTypes,
            count(isColocalisedVec) AS cnt
        FROM
            (
                SELECT
                    leftStudyLocusId,
                    list_distinct(list_sort(list(rightStudyType))) AS isColocalisedVec
                FROM
                    gwas_cs_colocalised
                GROUP BY
                    leftStudyLocusId
            )
        GROUP BY
            isColocalisedVec
        ORDER BY
            cnt DESC
    );

COMMIT;

BEGIN TRANSACTION;

/**
 * View describing how many GWAS credible sets colocalise with other study types
 */
CREATE VIEW gwas_colocalisation AS (
    SELECT
        studyType,
        round(sum(percentage), 2) || '%' AS totalPercentage
    FROM
        (
            SELECT
                unnest(colocalisedStudyTypes) AS studyType,
                percentage
            FROM
                (
                    SELECT
                        CASE
                            WHEN ((len(colocalisedStudyTypes) = 0)) THEN (list_value('notColocalised'))
                            ELSE colocalisedStudyTypes
                        END AS colocalisedStudyTypes,
                        cnt,
                        pct,
                        percentage
                    FROM
                        colocalisation_stats_view
                )
        )
    GROUP BY
        studyType
    ORDER BY
        totalPercentage DESC
);

COMMIT;