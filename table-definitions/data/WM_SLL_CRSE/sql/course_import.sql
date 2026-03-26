-- Watermark Course Import. Pulled 2/24/26 Gabriel Berres
SELECT DISTINCT
    scbcrse_subj_code
    || ' '
    || scbcrse_crse_numb  AS "course_catalog_code",
    scbcrse_title         AS "course_name",
    wm_sll_crse_node_name AS "organization_code",
    scbcrse_subj_code     AS "subject_code",
    scbcrse_crse_numb     AS "course_number",
    ''                    AS "course_description",
    scbcrse_credit_hr_low AS "credits",
    substr(scbcrse_cipc_code, 2, 2) || '.' || substr(scbcrse_cipc_code, 3, 6) AS "Cip_code"
FROM
         (
        SELECT DISTINCT
            scbcrse_subj_code                                       AS w_scbcrse_subj_code,
            scbcrse_crse_numb                                       AS w_scbcrse_crse_numb,
            MAX(scbcrse_eff_term)
            OVER(PARTITION BY scbcrse_subj_code, scbcrse_crse_numb) AS w_scbcrse_eff_term
        FROM
            scbcrse
    ) w_scbcrse
    JOIN scbcrse ON scbcrse_subj_code = w_scbcrse_subj_code
                    AND scbcrse_crse_numb = w_scbcrse_crse_numb
                    AND scbcrse_eff_term = w_scbcrse_eff_term
    JOIN stvdept ON stvdept_code = scbcrse_dept_code
    JOIN nsudev.wm_sll_crse ON wm_sll_crse_crse_numb = scbcrse_crse_numb
                               AND wm_sll_crse_subj_code = scbcrse_subj_code
                               AND wm_sll_crse_coll_code IN ('ED', 'BT', '00')
ORDER BY
    1
