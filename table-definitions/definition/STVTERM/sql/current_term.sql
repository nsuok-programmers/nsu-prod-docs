-- Current term with roll forward in the event of intercession (between terms).
-- 4/9/26 Gabriel Berres
SELECT DISTINCT
    MIN(stvterm_code)
FROM
    stvterm
WHERE
    stvterm_end_date > sysdate