/*
 Trans enhancer effects based on the mismatch between enhancer and target gene.
 */
CREATE VIEW trans_enhancers AS WITH e AS (
  SELECT
    DISTINCT geneId AS id,
    chromosome,
    "start" AS istart,
    "end" AS iend
  FROM
    enhancer_to_gene
),
x AS (
  SELECT
    DISTINCT id,
    canonicalTranscript.chromosome
  FROM
    target
)
SELECT
  *
FROM
  (
    SELECT
      e.id,
      e.chromosome AS ichr,
      istart,
      iend,
      x.chromosome AS tchr
    FROM
      e
      INNER JOIN x USING (id)
  )
WHERE
  (tchr != ichr);