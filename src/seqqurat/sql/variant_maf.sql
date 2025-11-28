-- The task is to build a view dataset that will contain the relevant information
-- Question: Should I limit to cisQTLs? - retain cisQTLs and transQTLs
-- Question: What ancestry to use when we have a qtl study without the ldPopulation specified? - fallback to nfe
-- Question: What if there is no alleleFrequency ? - fallback to 0.0
/*  Macro to extract the major population from the study table ldPopulationStructure field
 *  This macro will extract the population that has the highest relativeSampleSize
 *  In case multiple populations have the same sample size (highly unprobable) function 
 *  chooses the population that is specified by the `defaultMajorPopulationName` parameter
 *  In case the ldPopulationStructure is empty, the table will return Null.
 * Args:
 *      ldPopulationStructure - array [ structure { VARCHAR ldPopulation, DOUBLE relativeSampleSize  } ] Derived from `study` table.
 *      defaultMajorPopulationName - VARCHAR - Representing the default major allele when there is a tie (nfe should the used)
 * Returns:
 *      structure { VARCHAR ldPopulation, DOUBLE relativeSampleSize  } - Major ancestry for a study based on relativeSampleSize.
 */
CREATE
OR REPLACE MACRO major_ld_population_in_study(
  ldPopulationStructure,
  defaultMajorPopulationName
) AS CASE
  WHEN len(ldPopulationStructure) > 0 THEN list_reduce(
    ldPopulationStructure,
    (x1, x2) -> CASE
      WHEN x1.relativeSampleSize > x2.relativeSampleSize THEN x1
      WHEN x1.relativeSampleSize < x2.relativeSampleSize THEN x2
      WHEN (
        x1.relativeSampleSize = x2.relativeSampleSize
        AND x1.ldPopulation = defaultMajorPopulationName
      ) THEN x1
      WHEN (
        x1.relativeSampleSize = x2.relativeSampleSize
        AND x2.ldPopulation = defaultMajorPopulationName
      ) THEN x2 -- Case when both populations sample size is equal and they both are not default major
      ELSE x1
    END
  )
  ELSE Null
END;

CREATE
OR REPLACE MACRO fallback_to_nfe(majorLdPopulation) AS CASE
  WHEN majorLdPopulation is Null THEN struct_pack(ldPopulation := 'nfe', relativeSampleSize := 0.0)
  ELSE majorLdPopulation
END;

/* 
 * Macro to extract the major population allele frequency from the `variant` table allele frequencies.
 * !NOTE: The ldPopulationStructure.ldPopulation values does not contain the `_adj` as opposite to `variant` table `alleleFrequencies` field
 * Args: 
 *      majorLdPopulation - structure { VARCHAR ldPopulation, DOUBLE relativeSampleSize  } - Representing major population from the `major_ld_population_in_study` macro.
 *      alleleFrequencies - array [ structure { VARCHAR populationName, DOUBLE alleleFrequency } ] - Representing population allelic frequencies, derived from `variant` table. 
 * Returns:
 *      array [structure { VARCHAR populationName, DOUBLE alleleFrequency }] - Limited to the major ancestry or empty array in case the populationFrequency is missing.
 */
CREATE
OR REPLACE MACRO major_population_allele_freq(majorLdPopulation, alleleFrequencies) AS list_filter(
  alleleFrequencies,
  x -> replace(x.populationName, '_adj', '') = majorLdPopulation.ldPopulation
);

/* 
 * Macro to calculate MAF from alleleFrequency
 * Args:
 *      alleleFrequencies - array [ structure { VARCHAR populationName, DOUBLE alleleFrequency } ] - Should be limited to the major ancestry first.
 * Returns: 
 *      DOUBLE - Minor Allele Frequency.
 */
CREATE
OR REPLACE MACRO variant_maf(alleleFrequencies) AS CASE
  WHEN (
    len(alleleFrequencies) = 1
    AND alleleFrequencies [1].alleleFrequency > 0.5
  ) THEN 1.0 - alleleFrequencies [1].alleleFrequency
  WHEN (
    len(alleleFrequencies) = 1
    AND alleleFrequencies [1].alleleFrequency <= 0.5
  ) THEN alleleFrequencies [1].alleleFrequency
  WHEN len(alleleFrequencies) = 0 THEN 0.0
  ELSE Null
END;

/* View to store the information about the credible set lead variants */
CREATE
OR REPLACE VIEW lead_variant_maf AS (
  SELECT
    credible_set.studyId,
    credible_set.studyLocusId,
    credible_set.variantId,
    credible_set.beta,
    credible_set.zScore,
    credible_set.pValueMantissa,
    credible_set.pValueExponent,
    credible_set.standardError,
    credible_set.finemappingMethod,
    credible_set.studyType,
    length(credible_set.locus) as credibleSetSize,
    si.nCases,
    si.nControls,
    si.nSamples,
    fallback_to_nfe(
      major_ld_population_in_study(si.ldPopulationStructure, 'nfe')
    ) AS majorPopulation,
    variant_maf(
      major_population_allele_freq(majorPopulation, vi.alleleFrequencies)
    ) AS majorPopulationMAF,
    major_population_allele_freq(majorPopulation, vi.alleleFrequencies) AS majorPopulationAlleleFrequency
  FROM
    credible_set
    LEFT JOIN (
      SELECT
        study.studyId,
        study.nSamples,
        study.nCases,
        study.nControls,
        study.ldPopulationStructure,
      FROM
        study
    ) AS si ON credible_set.studyId = si.studyId
    LEFT JOIN (
      SELECT
        variant.variantId,
        variant.alleleFrequencies
      FROM
        variant
    ) AS vi ON vi.variantId = credible_set.variantId
)