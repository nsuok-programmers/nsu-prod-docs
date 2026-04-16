-- Students Who Cannot Register
-- written by Nathan Beene 4/14/26
SELECT
    sgbstdn_pidm,
    spriden_first_name,
    spriden_last_name,
    CASE
        WHEN stvastd_prevent_reg_ind = 'Y' THEN 'N'
        ELSE 'Y'
    END as can_register
FROM
    sgbstdn
LEFT JOIN
    spriden ON spriden_pidm = sgbstdn_pidm
LEFT JOIN
    stvastd ON sgbstdn_astd_code = stvastd_code
WHERE
    spriden_change_ind IS NULL
    AND stvastd_prevent_reg_ind = 'Y'
ORDER BY
    spriden_last_name, spriden_first_name;