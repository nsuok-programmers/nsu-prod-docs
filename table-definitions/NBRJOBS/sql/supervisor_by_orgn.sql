-- Supervisor by ORGN. 3/25/26 Gabriel Berres
SELECT DISTINCT
    spriden_last_name || ', ' || spriden_first_name manager_name,
    gobtpac_external_user || '@nsuok.edu' manager_email
FROM
    ftvorgn
    JOIN spriden ON spriden_pidm = ftvorgn_fmgr_code_pidm
        AND spriden_change_ind IS NULL
    JOIN gobtpac ON gobtpac_pidm = ftvorgn_fmgr_code_pidm
WHERE
    ftvorgn_orgn_code = 'T60101' -- Enterprise. Replace with your ORGN
    AND ftvorgn_eff_date = 
    (
        SELECT 
            MAX(x.ftvorgn_eff_date)
        FROM
            ftvorgn x
        WHERE
            x.ftvorgn_orgn_code = ftvorgn.ftvorgn_orgn_code
    )-- Only get most recent manager