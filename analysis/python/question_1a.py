import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")
q1a = pd.read_sql("""
    SELECT
        iso3,
        year,
        rate_total
    FROM labour_participation
    WHERE iso3 IN ('USA', 'DEU')
        AND rate_total IS NOT NULL
    ORDER BY iso3, year;
""", conn)

fig, ax = plt.subplots(figsize=(10, 6))

for country, group in q1a.groupby("iso3"):
    ax.plot(group["year"], group["rate_total"], label=country, linewidth=2)

ax.set_title("Labour Force Participation Rate: USA vs Germany (1990–2023)")
ax.set_xlabel("Year")
ax.set_ylabel("Participation Rate (%)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q1a_participation.png", dpi=150)
plt.show()

conn.close()
