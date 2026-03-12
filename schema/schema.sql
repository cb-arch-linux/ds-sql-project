-- Labour Market Database Schema

-- Drop tables if they exist for repeatability
DROP TABLE IF EXISTS sector_employment;
DROP TABLE IF EXISTS labour_shocks;
DROP TABLE IF EXISTS age_participation;
DROP TABLE IF EXISTS labour_participation;
DROP TABLE IF EXISTS countries;

-- Master countries table
CREATE TABLE countries (
    iso3          CHAR(3)       PRIMARY KEY,
    country_name  VARCHAR(100)  NOT NULL,
    region        VARCHAR(100),
    income_group  VARCHAR(50)
);

-- Labour force participation rates (overall, male, female) by year
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

-- Youth participation rates
CREATE TABLE age_participation (
    id             INTEGER       PRIMARY KEY,
    iso3           CHAR(3)       NOT NULL REFERENCES countries(iso3),
    year           SMALLINT      NOT NULL,
    age_group      VARCHAR(20)   NOT NULL, -- '15-24', '15-24 male', '15-24 female'
    participation  NUMERIC(5,2),
    UNIQUE (iso3, year, age_group)
);

-- Economic shocks / events for annotation
CREATE TABLE labour_shocks (
    id          INTEGER       PRIMARY KEY,
    shock_year  SMALLINT      NOT NULL,
    shock_name  VARCHAR(100)  NOT NULL,
    description TEXT
);

-- Sector employment shares (% of total employment)
CREATE TABLE sector_employment (
    id              INTEGER       PRIMARY KEY,
    iso3            CHAR(3)       NOT NULL REFERENCES countries(iso3),
    year            SMALLINT      NOT NULL,
    sector          VARCHAR(50)   NOT NULL,  -- 'Agriculture','Industry','Services'
    employment_pct  NUMERIC(5,2),
    UNIQUE (iso3, year, sector)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_participation_country_year ON labour_participation(iso3, year);
CREATE INDEX IF NOT EXISTS idx_age_country_year           ON age_participation(iso3, year);
CREATE INDEX IF NOT EXISTS idx_sector_country_year        ON sector_employment(iso3, year);

-- Insert known economic shocks
INSERT INTO labour_shocks (shock_year, shock_name, description) VALUES
  (2001, 'Dot-com Bust',            'Collapse of the dot-com bubble; mild recession in advanced economies'),
  (2008, 'Global Financial Crisis', 'Severe global recession triggered by US subprime mortgage crisis'),
  (2009, 'GFC Trough',              'Peak unemployment in most OECD countries following GFC'),
  (2011, 'Euro Debt Crisis',        'Sovereign debt crisis in eurozone periphery'),
  (2020, 'COVID-19 Pandemic',       'Global pandemic causing historic labour market disruptions');

