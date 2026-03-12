import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")

q5b = pd.read_sql("""
    SELECT iso3, year, sector, employment_pct
    FROM sector_employment
    WHERE iso3 IN ('USA', 'DEU')
        AND employment_pct IS NOT NULL
    ORDER BY iso3, year, sector
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
sector_colors = {"Agriculture": "green", "Industry": "orange", "Services": "blue"}

for ax, (country, group) in zip(axes, q5b.groupby("iso3")):
    pivot = group.pivot(index="year", columns="sector", values="employment_pct").fillna(0)
    pivot = pivot[["Agriculture", "Industry", "Services"]]  # consistent order
    ax.stackplot(pivot.index,
                 [pivot[s] for s in pivot.columns],
                 labels=pivot.columns,
                 colors=[sector_colors[s] for s in pivot.columns],
                 alpha=0.85)
    ax.set_title(country)
    ax.set_xlabel("Year")
    ax.grid(True, alpha=0.3)

axes[0].set_ylabel("Employment Share (%)")
handles = [plt.Rectangle((0, 0), 1, 1, color=sector_colors[s]) for s in ["Agriculture", "Industry", "Services"]]
fig.legend(handles, ["Agriculture", "Industry", "Services"], loc="upper right")
fig.suptitle("Sector Employment Shares Over Time", fontsize=13)

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q5b_sectors.png", dpi=150)
plt.show()

conn.close()