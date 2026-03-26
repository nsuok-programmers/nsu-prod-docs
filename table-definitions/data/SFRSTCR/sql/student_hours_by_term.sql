-- 3/2/26 Gabriel Berres
SELECT DISTINCT
    sfrstcr_pidm,
    spriden_last_name || ', ' || spriden_first_name student,
    SUM(sfrstcr_credit_hr) OVER(PARTITION BY sfrstcr_pidm) sum_enrolled
FROM
    sfrstcr
    JOIN spriden ON spriden_pidm = sfrstcr_pidm
        AND spriden_change_ind IS NULL
WHERE
    sfrstcr_term_code = '202630'
    AND sfrstcr_rsts_code IN ('RE', 'RW')
ORDER BY 2
