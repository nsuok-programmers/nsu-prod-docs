SELECT
    shrdgmr_pidm,
    shrdgmr_grad_date,
    stvterm_code
FROM
    shrdgmr
JOIN
    stvterm ON shrdgmr_grad_date BETWEEN stvterm_start_date AND stvterm_end_date + 20 -- Leave room for late graduation dates to be entered
WHERE
    stvterm_code = :term_code
