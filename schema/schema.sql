-- Labour Market Database Schema

-- Defines the relational database schema for the labour market
-- analysis project. All data is sourced from the World Bank
-- World Development Indicators API and loaded by fetch_worldbank.py.
--
-- The schema follows normalisation principles: each table describes
-- one thing, and the same fact is stored in one place only. Country
-- metadata is stored once in the countries table and referenced by
-- foreign key in all other tables, so updates only need to be made
-- in one place.
--
-- Run this file before fetch_worldbank.py to create the database
-- structure. Tables are dropped and recreated on each run so the
-- schema can be reapplied cleanly during development.
--
-- Tables:
--     countries            - Master list of countries with region and income group
--     labour_participation - Overall, male and female participation rates by year
--     age_participation    - Youth participation rates by age group and gender
--     labour_shocks        - Known economic events for chart annotation
--     sector_employment    - Employment shares by sector and year

-- Drop tables in reverse dependency order so foreign key references are removed before the tables they point to. 
-- Without this order, dropping countries before the tables that reference it would fail.
DROP TABLE IF EXISTS sector_employment;
DROP TABLE IF EXISTS labour_shocks;
DROP TABLE IF EXISTS age_participation;
DROP TABLE IF EXISTS labour_participation;
DROP TABLE IF EXISTS countries;

-- Master countries table storing one row per country.
-- iso3 is standard and serves as the primary key and foreign key target for all other tables. 
-- region and income_group are nullable as some World Bank entries do not carry this metadata.
CREATE TABLE countries (
    iso3          CHAR(3)       PRIMARY KEY,
    country_name  VARCHAR(100)  NOT NULL,
    region        VARCHAR(100),
    income_group  VARCHAR(50)
);

-- Overall, male and female labour force participation rates by country and year.
-- gender_gap is a computed column derived automatically from rate_male minus rate_female and is never inserted directly. 
-- The three rate columns are nullable as some country-year combinations have no World Bank estimate.
-- The UNIQUE constraint on iso3 and year enforces one row per country per year.
CREATE TABLE labour_participation (
    id             INTEGER       PRIMARY KEY,
    iso3           CHAR(3)       NOT NULL REFERENCES countries(iso3),
    year           SMALLINT      NOT NULL,
    rate_total     NUMERIC(5,2),   -- SL.TLF.CACT.ZS
    rate_male      NUMERIC(5,2),   -- SL.TLF.CACT.MA.ZS
    rate_female    NUMERIC(5,2),   -- SL.TLF.CACT.FE.ZS
    gender_gap     NUMERIC(5,2)  GENERATED ALWAYS AS (rate_male - rate_female) STORED,
    UNIQUE (iso3, year)
);

-- Youth labour force participation rates broken down by age group and gender.
-- The age_group column differentiates the total, male and female breakdowns stored as separate rows in long format.
-- participation is nullable as some country-year-group combinations have no World Bank estimate. 
-- NULL is more accurate than zero for missing data.
-- The UNIQUE constraint on iso3, year and age_group enforces one row per country, year and demographic group combination.
CREATE TABLE age_participation (
    id             INTEGER       PRIMARY KEY,
    iso3           CHAR(3)       NOT NULL REFERENCES countries(iso3),
    year           SMALLINT      NOT NULL,
    age_group      VARCHAR(20)   NOT NULL, -- '15-24', '15-24 male', '15-24 female'
    participation  NUMERIC(5,2),
    UNIQUE (iso3, year, age_group)
);

-- Known economic shocks and events used to annotate charts with context.
-- This table is populated by static INSERT statements below rather than the World Bank API, 
-- as these events are fixed reference points rather than measured indicators.
CREATE TABLE labour_shocks (
    id          INTEGER       PRIMARY KEY,
    shock_year  SMALLINT      NOT NULL,
    shock_name  VARCHAR(100)  NOT NULL,
    description TEXT
);

-- Sector employment shares as a percentage of total employment, stored in long format with one row per country, year and sector combination.
-- The three sectors are Agriculture, Industry and Services. 
-- Together they should sum to 100 for every country-year, which is verified by the data quality check in question_5a.py.
-- employment_pct is nullable as some country-year combinations have no World Bank estimate. 
-- The UNIQUE constraint on iso3, year and sector enforces one row per country, year and sector combination.
CREATE TABLE sector_employment (
    id              INTEGER       PRIMARY KEY,
    iso3            CHAR(3)       NOT NULL REFERENCES countries(iso3),
    year            SMALLINT      NOT NULL,
    sector          VARCHAR(50)   NOT NULL,  -- 'Agriculture','Industry','Services'
    employment_pct  NUMERIC(5,2),
    UNIQUE (iso3, year, sector)
);

-- Indexes on the most commonly filtered column combinations to speed up queries that filter or join on country and year. 
-- Without indexes, SQLite performs a full table scan for every query, which slows down significantly as row counts grow. 
-- IF NOT EXISTS prevents errors if the schema is rerun.
CREATE INDEX IF NOT EXISTS idx_participation_country_year ON labour_participation(iso3, year);
CREATE INDEX IF NOT EXISTS idx_age_country_year           ON age_participation(iso3, year);
CREATE INDEX IF NOT EXISTS idx_sector_country_year        ON sector_employment(iso3, year);

-- Static reference data for known economic shocks inserted once at schema creation time. 
-- These events are used to provide historical context when interpreting participation rate trends in the analysis.
INSERT INTO labour_shocks (shock_year, shock_name, description) VALUES
  (2001, 'Dot-com Bust',            'Collapse of the dot-com bubble; mild recession in advanced economies'),
  (2008, 'Global Financial Crisis', 'Severe global recession triggered by US subprime mortgage crisis'),
  (2009, 'GFC Trough',              'Peak unemployment in most OECD countries following GFC'),
  (2011, 'Euro Debt Crisis',        'Sovereign debt crisis in eurozone periphery'),
  (2020, 'COVID-19 Pandemic',       'Global pandemic causing historic labour market disruptions');

