BEGIN TRANSACTION;

CREATE VIEW study_statistics AS
SELECT
    studyType,
    cnt,
    ((cnt / sum(cnt) OVER ()) * 100) AS pct,
    (
        round(((cnt / sum(cnt) OVER ()) * 100), 2) || '%'
    ) AS percentage
FROM
    (
        SELECT
            studyType,
            count_star() AS cnt
        FROM
            study
        GROUP BY
            studyType
    )
ORDER BY
    cnt DESC;

COMMIT;