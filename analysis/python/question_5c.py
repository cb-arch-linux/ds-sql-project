import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")

q5c = pd.read_sql("""
    SELECT
        a.sector,
        ROUND(a.employment_pct, 2)                   AS us_pct,
        ROUND(b.employment_pct, 2)                   AS de_pct,
        ROUND(a.employment_pct - b.employment_pct, 2) AS difference
    FROM sector_employment AS a
    INNER JOIN sector_employment AS b
        ON a.year = b.year
        AND a.sector = b.sector
        AND b.iso3 = 'DEU'
    WHERE a.iso3 = 'USA'
        AND a.year = 2023
    ORDER BY difference DESC
""", conn)

fig, ax = plt.subplots(figsize=(8, 4))
colors = ["blue" if d >= 0 else "red" for d in q5c["difference"]]

ax.barh(q5c["sector"], q5c["difference"], color=colors, alpha=0.85)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Sector Employment Difference in 2023\nUSA minus Germany (percentage points)")
ax.set_xlabel("Difference (percentage points)")
ax.grid(True, alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q5c_sector_diff.png", dpi=150)
plt.show()

conn.close()