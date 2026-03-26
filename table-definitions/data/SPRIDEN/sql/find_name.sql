SELECT DISTINCT
    spriden_id,
    spriden_last_name,
    spriden_first_name,
    spriden_mi
FROM
    spriden
WHERE
    spriden_change_ind IS NULL;
