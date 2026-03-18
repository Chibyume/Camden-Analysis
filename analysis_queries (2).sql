-- Camden ZIP Code Analysis -- v2
-- all queries run directly against fact_socioeconomic, no joins needed


-- 1. income snapshot for 2022 ranked highest to lowest
SELECT
    zip_code,
    median_income,
    poverty_rate,
    unemployment_rate
FROM fact_socioeconomic
WHERE year_id = 2022
ORDER BY median_income DESC;


-- 2. poverty vs unemployment vs education -- the core correlation view
SELECT
    zip_code,
    poverty_rate,
    unemployment_rate,
    hs_grad_rate,
    snap_rate,
    uninsured_rate
FROM fact_socioeconomic
WHERE year_id = 2022
ORDER BY poverty_rate DESC;


-- 3. rent burden -- monthly rent as a percentage of monthly income
SELECT
    zip_code,
    median_gross_rent,
    median_income,
    ROUND((median_gross_rent / NULLIF(median_income / 12, 0)) * 100, 1) AS rent_burden_pct
FROM fact_socioeconomic
WHERE year_id = 2022
  AND median_income IS NOT NULL
  AND median_gross_rent IS NOT NULL
ORDER BY rent_burden_pct DESC;


-- 4. poverty rate trend across all three years
SELECT
    zip_code,
    MAX(CASE WHEN year_id = 2019 THEN poverty_rate END) AS poverty_2019,
    MAX(CASE WHEN year_id = 2021 THEN poverty_rate END) AS poverty_2021,
    MAX(CASE WHEN year_id = 2022 THEN poverty_rate END) AS poverty_2022,
    ROUND(
        MAX(CASE WHEN year_id = 2022 THEN poverty_rate END) -
        MAX(CASE WHEN year_id = 2019 THEN poverty_rate END),
    1) AS change_2019_to_2022
FROM fact_socioeconomic
GROUP BY zip_code
ORDER BY change_2019_to_2022;


-- 5. income trend across all three years
SELECT
    zip_code,
    MAX(CASE WHEN year_id = 2019 THEN median_income END) AS income_2019,
    MAX(CASE WHEN year_id = 2021 THEN median_income END) AS income_2021,
    MAX(CASE WHEN year_id = 2022 THEN median_income END) AS income_2022,
    ROUND(
        ((MAX(CASE WHEN year_id = 2022 THEN median_income END) -
          MAX(CASE WHEN year_id = 2019 THEN median_income END)) /
         NULLIF(MAX(CASE WHEN year_id = 2019 THEN median_income END), 0)) * 100,
    1) AS pct_change
FROM fact_socioeconomic
GROUP BY zip_code
ORDER BY pct_change DESC;


-- 6. demographic breakdown with income and poverty overlay
SELECT
    zip_code,
    pct_black,
    pct_hispanic,
    pct_white,
    poverty_rate,
    median_income
FROM fact_socioeconomic
WHERE year_id = 2022
ORDER BY zip_code;


-- 7. hardship index -- composite of five deprivation indicators
--    higher score = more hardship across the board
SELECT
    zip_code,
    poverty_rate,
    unemployment_rate,
    uninsured_rate,
    snap_rate,
    no_vehicle_pct,
    ROUND(
        (poverty_rate + unemployment_rate + uninsured_rate +
         snap_rate + no_vehicle_pct) / 5,
    1) AS hardship_index
FROM fact_socioeconomic
WHERE year_id = 2022
ORDER BY hardship_index DESC;


-- 8. full summary view -- connect this directly to tableau
SELECT
    zip_code,
    year_id AS year,
    median_income,
    poverty_rate,
    unemployment_rate,
    hs_grad_rate,
    uninsured_rate,
    snap_rate,
    median_gross_rent,
    no_vehicle_pct,
    pct_black,
    pct_hispanic,
    pct_white,
    ROUND((median_gross_rent / NULLIF(median_income / 12, 0)) * 100, 1) AS rent_burden_pct,
    ROUND((poverty_rate + unemployment_rate + uninsured_rate + snap_rate + no_vehicle_pct) / 5, 1) AS hardship_index
FROM fact_socioeconomic
ORDER BY zip_code, year_id;
