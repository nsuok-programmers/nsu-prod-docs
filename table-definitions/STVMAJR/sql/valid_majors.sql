-- Valid majors. 3/25/26 berresg
SELECT DISTINCT
    stvmajr_code,
    stvmajr_desc
FROM
    stvmajr
WHERE
    stvmajr_valid_major_ind = 'Y' 
ORDER BY 1;