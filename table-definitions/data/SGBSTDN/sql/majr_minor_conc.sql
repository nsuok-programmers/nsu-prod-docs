-- Get 1st major, minor, conc for most recent record per student. 2/23/26 Gabriel Berres
SELECT DISTINCT
    sgbstdn_pidm,
    sgbstdn_term_code_eff,
    sgbstdn_majr_code_1,
    ma_stvmajr.stvmajr_desc,
    sgbstdn_majr_code_minr_1,
    mn_stvmajr.stvmajr_desc,
    sgbstdn_majr_code_conc_1,
    co_stvmajr.stvmajr_desc
FROM
    sgbstdn
    JOIN stvmajr ma_stvmajr ON ma_stvmajr.stvmajr_code = sgbstdn_majr_code_1 -- Majors
    JOIN stvmajr mn_stvmajr ON mn_stvmajr.stvmajr_code = sgbstdn_majr_code_minr_1 -- Minors
    JOIN stvmajr co_stvmajr ON co_stvmajr.stvmajr_code = sgbstdn_majr_code_conc_1 -- Concentrations
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
