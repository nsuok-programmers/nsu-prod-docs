-- Students who started this semester. 4/21/26 Gabriel Berres
SELECT DISTINCT
gobtpac_external_user || '@nsuok.edu' email
FROM
sarappd
JOIN gobtpac ON gobtpac_pidm = sarappd_pidm
WHERE
-- First admitted term
(
SELECT DISTINCT
MIN(s2.sarappd_term_code_entry)
FROM
sarappd s2
WHERE
s2.sarappd_pidm = sarappd.sarappd_pidm
AND s2.sarappd_apdc_code NOT IN ('DN', 'GN', 'PD', 'PW')
) =
-- Current term
(
SELECT DISTINCT
MIN(stvterm_code)
FROM
stvterm
WHERE
stvterm_end_date > sysdate
)
ORDER BY 1 ASC;