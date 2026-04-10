-- 202630 Accounts with a balance
-- 4/10/26 Gabriel Berres
SELECT DISTINCT
    tbraccd_pidm,
    SUM(TBRACCD_AMOUNT) OVER(PARTITION BY tbraccd_pidm) balance
FROM
    tbraccd
WHERE
    tbraccd_balance > 0
    AND tbraccd_term_code = '202630'
ORDER BY 2 DESC;