-- All 202630 SFBETRM students
-- 4/14/26 Gabriel Berres
SELECT DISTINCT
    sfbetrm_pidm,
    sfbetrm_term_code,
    spriden_last_name || ', ' || spriden_first_name name,
    sfbetrm_ests_code
FROM
    sfbetrm
    JOIN spriden ON spriden_pidm = sfbetrm_pidm
        AND spriden_change_ind IS NULL
WHERE
    sfbetrm_term_code = '202630'
    AND sfbetrm_ests_code = 'EL';