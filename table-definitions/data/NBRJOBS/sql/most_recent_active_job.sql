-- Most recent Active job by PIDM. 3/25/26 Gabriel Berres
SELECT DISTINCT
    spriden_last_name || ', ' || spriden_first_name employee,
    nbrjobs_ecls_code ecls_code,
    nbrjobs_desc job_desc,
    nbrjobs_status status
FROM
    nbrjobs
    JOIN spriden ON spriden_pidm = nbrjobs_pidm
        AND spriden_change_ind IS NULL
    JOIN nbrbjob ON nbrbjob_pidm = nbrjobs_pidm
        AND nbrbjob_posn = nbrjobs_posn
        AND nbrbjob_contract_type = 'P'  -- Primary Job
WHERE
    nbrjobs_effective_date = 
    (
        SELECT DISTINCT
            MAX(n2.nbrjobs_effective_date)
        FROM
            nbrjobs n2
        WHERE
            n2.nbrjobs_pidm = nbrjobs.nbrjobs_pidm
            AND n2.nbrjobs_status = 'A'      
    )
    AND nbrjobs_status = 'A'
    AND nbrjobs_pidm = 228479 -- YOUR/employee pidm