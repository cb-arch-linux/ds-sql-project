-- Q1: Overall labour force participation rates (US & Germany)

-- Selects the total participation rate for the US (USA) and Germany (DEU).
-- The IS NOT NULL excludes years where the World Bank has no recorded value, as NULL in SQL is not equivalent to zero and would produce blank rows.
-- Results are ordered by country then year for consistent groupby behaviour when plotting.
SELECT
    iso3,
    year,
    rate_total
FROM labour_participation
WHERE iso3 IN ('USA', 'DEU')
    AND rate_total IS NOT NULL
ORDER BY iso3, year;


-- Self-join on labour_participation using two aliases: us for US rows and de for German rows. 
-- Joining on year ensures each output row contains both countries' rates for the same year, allowing the gap to be computed as a single expression in SQL.
-- INNER JOIN is used deliberately, if a year is missing for either country, that row is dropped entirely rather than returning a NULL gap that could be 
-- misread as zero.
-- Germany's filter is placed in the ON clause and the US filter in WHERE, which is the conventional pattern for self-joins in SQL.
-- ROUND(..., 2) is applied to all numeric outputs for clean display, though the underlying data remains unchanged in the database.
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

-- Q2: Gender gaps in labour force participation (US & Germany)

-- Male and female participation rates for both countries over time.
-- Both rate_male and rate_female must be non-null to ensure gender_gap is meaningful. 
-- Ordering by country then year produces consistent groupby behaviour when plotting.
SELECT
    iso3,
    year,
    rate_male,
    rate_female,
    gender_gap
FROM labour_participation
WHERE iso3 IN ('USA', 'DEU')
    AND rate_male IS NOT NULL
    AND rate_female IS NOT NULL
ORDER BY iso3, year;


-- Year-by-year comparison of gender gaps between the US and Germany using a self-join. 
-- Each output row contains both countries gender gaps for the same year, allowing direct comparison and the difference to be computed in a single expression.
-- INNER JOIN ensures only years where both countries have data are returned.
SELECT
    us.year,
    ROUND(us.gender_gap, 2)                     AS us_gap,
    ROUND(de.gender_gap, 2)                     AS de_gap,
    ROUND(us.gender_gap - de.gender_gap, 2)     AS gap_difference
FROM labour_participation AS us
INNER JOIN labour_participation AS de
    ON us.year = de.year
    AND de.iso3 = 'DEU'
WHERE us.iso3 = 'USA'
    AND us.gender_gap IS NOT NULL
    AND de.gender_gap IS NOT NULL
ORDER BY us.year;

-- Q3: Participation rates by age group (15-24 only)

-- Pivot query using CASE WHEN inside SUM to extract participation rates for four snapshot years into separate columns. 
-- For each country and age group combination returned by GROUP BY, the CASE WHEN tests whether the year matches the target.
-- If it does, the participation rate is returned; if not, NULL is returned.
-- SUM of a single non-null value alongside NULLs returns that value, effectively placing the rate for each specific year into its own column.
-- ELSE NULL is included to make the intent clear when reading the code.
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


-- Self-join on age_participation using two aliases: a for US rows and b for German rows. 
-- Joining on both year and age_group ensures rows are only paired when they represent the same year and the same age group.
-- INNER JOIN is used deliberately so that if either country is missing a rate for a particular age group or year, that row is dropped entirely rather than
-- returning a NULL difference that could be misread as zero.
-- Germany's filter is placed in the ON clause and the US filter in WHERE, which is the conventional pattern for self-joins in SQL.
-- ROUND(..., 2) is applied to all numeric outputs for clean display, though the underlying data remains unchanged in the database.
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

-- Q4: Impact of economic shocks on participation rates

-- Participation rates for both countries over time joined with the labour_shocks table to annotate shock years. 
-- LEFT JOIN retains all participation rate rows regardless of whether a shock occurred that year, with shock_name returning NULL for non-shock years.
SELECT
    lp.iso3,
    lp.year,
    lp.rate_total,
    ls.shock_name
FROM labour_participation AS lp
LEFT JOIN labour_shocks AS ls
    ON lp.year = ls.shock_year
WHERE lp.iso3 IN ('USA', 'DEU')
    AND lp.rate_total IS NOT NULL
ORDER BY lp.iso3, lp.year;


-- Year-on-year change in participation rate for each country to isolate the impact of shock years. 
-- A self-join on consecutive years (year = prev_year + 1) computes the change from one year to the next.
-- Shock years are joined to identify which changes coincide with known events.
-- INNER JOIN on consecutive years means the first year of data is excluded as there is no prior year to compare against.
SELECT
    curr.iso3,
    curr.year,
    ROUND(curr.rate_total, 2)                       AS rate,
    ROUND(curr.rate_total - prev.rate_total, 2)     AS yoy_change,
    ls.shock_name
FROM labour_participation AS curr
INNER JOIN labour_participation AS prev
    ON curr.iso3 = prev.iso3
    AND curr.year = prev.year + 1
LEFT JOIN labour_shocks AS ls
    ON curr.year = ls.shock_year
WHERE curr.iso3 IN ('USA', 'DEU')
    AND curr.rate_total IS NOT NULL
    AND prev.rate_total IS NOT NULL
ORDER BY curr.iso3, curr.year;

-- Q5: Sector employment shares (US & Germany)

-- Aggregates the three sector shares for each country and year using SUM and GROUP BY. 
-- ROUND(..., 1) is applied to smooth out minor floating point differences in the source data. 
-- The result should be 100.0 for every row if the data is complete and consistent.
SELECT
    iso3,
    year,
    ROUND(SUM(employment_pct), 1) AS total_pct
FROM sector_employment
WHERE iso3 IN ('USA', 'DEU')
GROUP BY iso3, year
ORDER BY iso3, year;


-- Pivot query using CASE WHEN inside SUM to place each sector's employment share into its own column. 
-- For each country and year combination returned by GROUP BY, the CASE WHEN tests whether the sector matches the target. 
-- If it does, the employment share is returned; if not, NULL is returned. 
-- SUM of a single non-null value alongside NULLs returns that value, effectively placing each sector's share 
-- into its own column without needing to reshape the data in Python.
-- IS NOT NULL in the WHERE clause excludes rows where the World Bank has no recorded value, 
-- as fillna(0) below is only intended to handle structural gaps in the result rather than treating genuinely missing data as zero employment.
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


-- Self-join on sector_employment using two aliases: a for US rows and b for German rows. 
-- Joining on both year and sector ensures rows are only paired when they represent the same year and the same sector.
-- INNER JOIN is used deliberately so that if either country is missing a sector in 2023, that row is dropped entirely rather than returning a NULL difference
-- that could distort the chart.
-- Germany's filter is placed in the ON clause and the US filter in WHERE.
-- ROUND(..., 2) is applied to all numeric outputs for clean display, though the underlying data remains unchanged in the database.
-- ORDER BY difference DESC means sectors where the US leads appear at the top of the chart and sectors where Germany leads appear at the bottom.
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
