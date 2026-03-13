-- Q1: Overall labour force participation rates (US & Germany)

-- Query 1a: Participation rates for both countries over time
SELECT
    iso3,
    year,
    rate_total
FROM labour_participation
WHERE iso3 IN ('USA', 'DEU')
    AND rate_total IS NOT NULL
ORDER BY iso3, year;


-- Query 1b: Year-by-year gap between US and Germany (self-join)
SELECT
    us.year,
    ROUND(us.rate_total, 2)               AS us_rate,
    ROUND(de.rate_total, 2)               AS de_rate,
    ROUND(us.rate_total - de.rate_total, 2) AS gap
FROM labour_participation AS us
INNER JOIN labour_participation AS de
    ON us.year = de.year
    AND de.iso3 = 'DEU'
WHERE us.iso3 = 'USA'
ORDER BY us.year;

-- Q3: Participation rates by age group (15-24 only)

-- Query 3a: Pivot — rates for selected years by age group
SELECT
    iso3,
    age_group,
    SUM(CASE WHEN year = 1995 THEN participation ELSE NULL END) AS y1995,
    SUM(CASE WHEN year = 2008 THEN participation ELSE NULL END) AS y2008,
    SUM(CASE WHEN year = 2019 THEN participation ELSE NULL END) AS y2019,
    SUM(CASE WHEN year = 2023 THEN participation ELSE NULL END) AS y2023
FROM age_participation
WHERE iso3 IN ('USA', 'DEU')
GROUP BY iso3, age_group
ORDER BY iso3, age_group;


-- Query 3b: US vs Germany difference by age group (self-join)
SELECT
    a.year,
    a.age_group,
    ROUND(a.participation, 2)               AS us_rate,
    ROUND(b.participation, 2)               AS de_rate,
    ROUND(a.participation - b.participation, 2) AS difference
FROM age_participation AS a
INNER JOIN age_participation AS b
    ON a.year = b.year
    AND a.age_group = b.age_group
    AND b.iso3 = 'DEU'
WHERE a.iso3 = 'USA'
ORDER BY difference DESC;

-- Q5: Sector employment shares (US & Germany)

-- Query 5a: Data quality check — sectors should sum to 100
SELECT
    iso3,
    year,
    ROUND(SUM(employment_pct), 1) AS total_pct
FROM sector_employment
WHERE iso3 IN ('USA', 'DEU')
GROUP BY iso3, year
ORDER BY iso3, year;


-- Query 5b: Pivot — sector shares for selected years
SELECT
    iso3,
    year,
        SUM(CASE WHEN sector = 'Agriculture' THEN employment_pct ELSE NULL END) AS Agriculture,
        SUM(CASE WHEN sector = 'Industry'    THEN employment_pct ELSE NULL END) AS Industry,
        SUM(CASE WHEN sector = 'Services'    THEN employment_pct ELSE NULL END) AS Services
FROM sector_employment
WHERE iso3 IN ('USA', 'DEU')
        AND employment_pct IS NOT NULL
GROUP BY iso3, year
ORDER BY iso3, year


-- Query 5c: US vs Germany sector difference in 2023 (self-join)
SELECT
    a.sector,
    ROUND(a.employment_pct, 2)               AS us_pct,
    ROUND(b.employment_pct, 2)               AS de_pct,
    ROUND(a.employment_pct - b.employment_pct, 2) AS difference
FROM sector_employment AS a
INNER JOIN sector_employment AS b
    ON a.year = b.year
    AND a.sector = b.sector
    AND b.iso3 = 'DEU'
WHERE a.iso3 = 'USA'
    AND a.year = 2023
ORDER BY difference DESC;
