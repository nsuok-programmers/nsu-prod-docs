-- Most recent PR address record
-- 4/14/26 Gabriel Berres
SELECT DISTINCT
    spriden_last_name || ', ' || spriden_first_name name,
    spraddr_atyp_code,
    spraddr_street_line1,
    spraddr_street_line2,
    spraddr_street_line3,
    spraddr_city,
    spraddr_stat_code,
    spraddr_zip
FROM
    spraddr
    JOIN spriden ON spriden_pidm = spraddr_pidm
        AND spriden_change_ind IS NULL
        AND spriden_entity_ind = 'P'
WHERE
    spraddr_atyp_code = 'PR'
    AND spraddr_seqno = 
    (
        SELECT DISTINCT
            MAX(s2.spraddr_seqno)
        FROM
            spraddr s2
        WHERE
            s2.spraddr_pidm = spraddr.spraddr_pidm
            AND s2.spraddr_atyp_code = spraddr.spraddr_atyp_code
    )
ORDER BY 1