-- Get most recent record per student. 2/23/26 Gabriel Berres
SELECT DISTINCT
    sgbstdn_pidm,
    sgbstdn_term_code_eff
FROM
    sgbstdn
WHERE
    -- To get most recent record for student
    sgbstdn_term_code_eff =
    (
        SELECT DISTINCT
            MAX(s2.sgbstdn_term_code_eff)
        FROM
            sgbstdn s2
        WHERE s2.sgbstdn_pidm = sgbstdn.sgbstdn_pidm -- Join to outer
    )
