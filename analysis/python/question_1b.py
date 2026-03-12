import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")
COLORS = {"USA": "blue", "DEU": "red"}

q1b = pd.read_sql("""
    SELECT
        us.year,
        ROUND(us.rate_total, 2)                 AS us_rate,
        ROUND(de.rate_total, 2)                 AS de_rate,
        ROUND(us.rate_total - de.rate_total, 2) AS gap
    FROM labour_participation AS us
    INNER JOIN labour_participation AS de
        ON us.year = de.year
        AND de.iso3 = 'DEU'
    WHERE us.iso3 = 'USA'
    ORDER BY us.year
""", conn)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(q1b["year"], q1b["us_rate"], label="USA",     linewidth=2, color=COLORS["USA"])
ax.plot(q1b["year"], q1b["de_rate"], label="Germany", linewidth=2, color=COLORS["DEU"])
ax.fill_between(q1b["year"], q1b["us_rate"], q1b["de_rate"], alpha=0.1, color="grey")
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

# Annotate the gap line
ax2 = ax.twinx()
ax2.plot(q1b["year"], q1b["gap"], label="Gap (USA - DEU)",
         linewidth=1.5, color="grey", linestyle="--")
ax2.set_ylabel("Gap (percentage points)")
ax2.axhline(0, color="black", linewidth=0.5)

ax.set_title("Participation Rate Gap: USA vs Germany")
ax.set_xlabel("Year")
ax.set_ylabel("Participation Rate (%)")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="lower left")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q1b_gap.png", dpi=150)
plt.show()

conn.close()