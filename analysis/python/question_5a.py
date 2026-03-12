import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")
COLORS = {"USA": "blue", "DEU": "red"}

q5a = pd.read_sql("""
    SELECT
        iso3,
        year,
        ROUND(SUM(employment_pct), 1) AS total_pct
    FROM sector_employment
    WHERE iso3 IN ('USA', 'DEU')
    GROUP BY iso3, year
    ORDER BY iso3, year
""", conn)

fig, ax = plt.subplots(figsize=(10, 4))
for country, group in q5a.groupby("iso3"):
    ax.plot(group["year"], group["total_pct"],
            label=country, linewidth=2, color=COLORS[country])
    
ax.axhline(100, color="green", linestyle="--", linewidth=1, label="Expected = 100")
ax.set_title("Sector Employment Data Quality Check")
ax.set_xlabel("Year")
ax.set_ylabel("Sum of Sector Shares (%)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q5a_quality.png", dpi=150)
plt.show()

conn.close()