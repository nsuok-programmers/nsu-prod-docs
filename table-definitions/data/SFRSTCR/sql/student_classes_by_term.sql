-- 3/2/26 Gabriel Berres
SELECT DISTINCT
    sfrstcr_pidm,
    spriden_last_name || ', ' || spriden_first_name student,
    sfrstcr_crn,
    scbcrse_title,
    sfrstcr_credit_hr,
    sfrstcr_rsts_code,
    stvrsts_desc
FROM
    sfrstcr
    JOIN stvrsts ON stvrsts_code = sfrstcr_rsts_code
    JOIN ssbsect ON ssbsect_crn = sfrstcr_crn
        AND ssbsect_term_code = sfrstcr_term_code
    JOIN scbcrse ON scbcrse_crse_numb = ssbsect_crse_numb
        AND scbcrse_subj_code = ssbsect_subj_code
    JOIN spriden ON spriden_pidm = sfrstcr_pidm
        AND spriden_change_ind IS NULL
WHERE
    sfrstcr_term_code = '202630'
    AND sfrstcr_rsts_code IN ('RE', 'RW')
ORDER BY 2
