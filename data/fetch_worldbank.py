import requests
import pandas as pd
import sqlite3
from functools import reduce

WB = "https://api.worldbank.org/v2/country/all/indicator"
PARAMS = {"format": "json", "per_page": 20000, "date": "1990:2023"}

# Fetch helpers 

def fetch(code, colname):
    r = requests.get(f"{WB}/{code}", params=PARAMS)
    result = r.json()
    if len(result) < 2 or not result[1]:
        print(f"  WARNING: no data returned for {code}, skipping")
        return pd.DataFrame(columns=["iso3", "year", colname])
    data = result[1]
    rows = [{"iso3": d["countryiso3code"], "year": int(d["date"]), colname: d["value"]}
            for d in data if d["countryiso3code"]]
    print(f"  {colname}: {len(rows):,} rows")
    return pd.DataFrame(rows)

def merge(frames):
    df = reduce(lambda a, b: pd.merge(a, b, on=["iso3", "year"], how="outer"), frames)
    return df[df["iso3"].str.len() == 3].copy()  # drop World Bank aggregates

# Countries 

print("Fetching countries...")
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
participation_df = merge([
    fetch("SL.TLF.CACT.ZS",    "rate_total"),
    fetch("SL.TLF.CACT.MA.ZS", "rate_male"),
    fetch("SL.TLF.CACT.FE.ZS", "rate_female"),
])
participation_df["gender_gap"] = participation_df["rate_male"] - participation_df["rate_female"]

# Youth participation

print("\nFetching age-group participation...")
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
age_df = pd.concat(age_frames, ignore_index=True)
age_df = age_df[age_df["iso3"].str.len() == 3]

# Sector employment 

print("\nFetching sector employment...")
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
sector_df = sector_df[sector_df["iso3"].str.len() == 3]

# Save to SQLite 

print("\nSaving to db...")
conn = sqlite3.connect("labour_market.db")

countries_df.to_sql("countries",               conn, if_exists="replace", index=False)
participation_df.to_sql("labour_participation", conn, if_exists="replace", index=False)
age_df.to_sql("age_participation",             conn, if_exists="replace", index=False)
sector_df.to_sql("sector_employment",          conn, if_exists="replace", index=False)

conn.close()
print("Done! Database saved to db")
