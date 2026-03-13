"""
Fetches labour market data from the World Bank World Development Indicators
API and loads it into a local SQLite database for analysis. The script
retrieves four datasets - countries, overall labour participation, youth
participation by gender, and sector employment shares - and writes each
to a separate table in the database.

The World Bank REST API requires no authentication and returns JSON responses. 
The per_page parameter is set to 20000 to retrieve all data in a single request.

This script must be run before any of the analysis or plotting scripts,
as it creates and populates the database they all depend on.

Indicators fetched:
    SL.TLF.CACT.ZS    - Labour force participation rate, total
    SL.TLF.CACT.MA.ZS - Labour force participation rate, male
    SL.TLF.CACT.FE.ZS - Labour force participation rate, female
    SL.TLF.ACTI.1524.ZS    - Youth participation rate, total (ages 15 to 24)
    SL.TLF.ACTI.1524.MA.ZS - Youth participation rate, male (ages 15 to 24)
    SL.TLF.ACTI.1524.FE.ZS - Youth participation rate, female (ages 15 to 24)
    SL.AGR.EMPL.ZS - Employment in agriculture (% of total employment)
    SL.IND.EMPL.ZS - Employment in industry (% of total employment)
    SL.SRV.EMPL.ZS - Employment in services (% of total employment)

Note on age group coverage:
    The World Bank API only provides participation rate data for the 15 to 24
    age group. Indicators for 25 to 54, 55 to 64 and 65 plus returned no data
    and were excluded. Only the 15 to 24 total, male and female breakdowns
    are loaded into the age_participation table.

Output:
    labour_market.db - SQLite database containing four tables:
    countries, labour_participation, age_participation, sector_employment

Dependencies:
    requests  - HTTP requests to the World Bank API
    pandas    - data manipulation and database loading
    sqlite3   - standard library
"""

import requests
import pandas as pd
import sqlite3
from functools import reduce

# Base URL for the World Bank indicator.
WB = "https://api.worldbank.org/v2/country/all/indicator"
PARAMS = {"format": "json", "per_page": 20000, "date": "1990:2023"}

# Fetch helpers 

def fetch(code, colname):
    """
    Fetches a single World Bank indicator for all countries and returns a DataFrame with columns iso3, year and the named column.

    If the API returns an empty response the function prints a warning and returns an empty DataFrame rather than raising an error, 
    allowing the calling code to continue without that indicator.

    Parameters
        code    - World Bank indicator code e.g. SL.TLF.CACT.ZS
        colname - Column name to assign to the indicator values in the DataFrame
    """
    r = requests.get(f"{WB}/{code}", params=PARAMS)
    result = r.json()

    # The World Bank API returns a two-element list: [metadata, data]. If the indicator does not exist or has no data, result[1] is absent or empty. 
    # This guard prevents an IndexError in those cases.
    if len(result) < 2 or not result[1]:
        print(f"  WARNING: no data returned for {code}, skipping")
        return pd.DataFrame(columns=["iso3", "year", colname])
    data = result[1]

    # Rows with no iso3 code are World Bank aggregate regions rather than individual countries and are excluded here. 
    # NULL values are retained as None so they load into SQLite as NULL rather than being dropped, 
    # preserving the country-year structure even where data is missing.
    rows = [{"iso3": d["countryiso3code"], "year": int(d["date"]), colname: d["value"]}
            for d in data if d["countryiso3code"]]
    print(f"  {colname}: {len(rows):,} rows")
    return pd.DataFrame(rows)

def merge(frames):
    """
    Outer merges a list of DataFrames on iso3 and year, then filters to rows where iso3 is exactly three characters to remove World Bank
    aggregate rows such as regional and income group totals.

    Parameters
        frames - List of DataFrames each containing iso3, year and one indicator column
    """
    df = reduce(lambda a, b: pd.merge(a, b, on=["iso3", "year"], how="outer"), frames)

    # World Bank aggregate codes such as EAP (East Asia Pacific) are longer than three characters or do not conform to iso3 format.
    # Filtering to exactly three characters removes these aggregates while retaining all individual country rows.
    return df[df["iso3"].str.len() == 3].copy() 

# Countries 

print("Fetching countries...")

# The country endpoint returns metadata for all World Bank members including aggregates. 
# Filtering to iso3 codes of exactly three characters retains only individual countries and excludes regional groupings.
r = requests.get("https://api.worldbank.org/v2/country", params={"format": "json", "per_page": 500})
countries = [
    {"iso3": c["id"], "country_name": c["name"],
     "region": c["region"]["value"], "income_group": c["incomeLevel"]["value"]}
    for c in r.json()[1]
    if len(c["id"]) == 3  # drop aggregates
]
countries_df = pd.DataFrame(countries)
print(f"  {len(countries_df):,} countries")

# Labour participation (overall, male, female) 

print("\nFetching labour participation...")

# Three indicators are fetched separately and outer merged on iso3 and year so that a country-year row is retained even if only one or two of the
# three rates are available for that combination.
participation_df = merge([
    fetch("SL.TLF.CACT.ZS",    "rate_total"),
    fetch("SL.TLF.CACT.MA.ZS", "rate_male"),
    fetch("SL.TLF.CACT.FE.ZS", "rate_female"),
])

# gender_gap is derived in Python rather than stored in the source data. It replicates the GENERATED ALWAYS AS column defined in schema.sql,
# since to_sql writes directly to the table without enforcing that constraint.
participation_df["gender_gap"] = participation_df["rate_male"] - participation_df["rate_female"]

# Youth participation

print("\nFetching age-group participation...")

# Each indicator represents a different demographic breakdown of the 15 to 24 age group. 
# Each is fetched into a long-format DataFrame with an age_group column added before concatenating, 
# so all three breakdowns share one table with age_group as a differentiating column.
age_indicators = {
    "SL.TLF.ACTI.1524.ZS":    "15-24",
    "SL.TLF.ACTI.1524.MA.ZS": "15-24 male",
    "SL.TLF.ACTI.1524.FE.ZS": "15-24 female",
}
age_frames = []
for code, age_group in age_indicators.items():
    df = fetch(code, "participation")
    df["age_group"] = age_group
    age_frames.append(df)

# Concatenate all age group frames into a single long-format DataFrame.
age_df = pd.concat(age_frames, ignore_index=True)

# Sector employment 

print("\nFetching sector employment...")

# The same long-format pattern is used. Each sector is fetched separately with a sector column added before concatenating,
# so all three sectors share one table with sector as a differentiating column.
sector_indicators = {
    "SL.AGR.EMPL.ZS": "Agriculture",
    "SL.IND.EMPL.ZS": "Industry",
    "SL.SRV.EMPL.ZS": "Services",
}
sector_frames = []
for code, sector in sector_indicators.items():
    df = fetch(code, "employment_pct")
    df["sector"] = sector
    sector_frames.append(df)
sector_df = pd.concat(sector_frames, ignore_index=True)

# Save to SQLite 

print("\nSaving to labour_market.db...")
conn = sqlite3.connect("labour_market.db")

# if_exists="replace" drops and recreates each table on every run so the database is always a clean reflection of the latest API data.
# index=False prevents pandas from writing its own integer index as a column.
countries_df.to_sql("countries",               conn, if_exists="replace", index=False)
participation_df.to_sql("labour_participation", conn, if_exists="replace", index=False)
age_df.to_sql("age_participation",             conn, if_exists="replace", index=False)
sector_df.to_sql("sector_employment",          conn, if_exists="replace", index=False)

# Explicitly close the connection as good practice
conn.close()
print("Done! Database saved to labour_market.db")
