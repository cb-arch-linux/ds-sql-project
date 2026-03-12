import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")

q3b = pd.read_sql("""
    SELECT
        a.year,
        a.age_group,
        ROUND(a.participation, 2)                   AS us_rate,
        ROUND(b.participation, 2)                   AS de_rate,
        ROUND(a.participation - b.participation, 2) AS difference
    FROM age_participation AS a
    INNER JOIN age_participation AS b
        ON a.year = b.year
        AND a.age_group = b.age_group
        AND b.iso3 = 'DEU'
    WHERE a.iso3 = 'USA'
    ORDER BY difference DESC
""", conn)

# Plot for most recent year available
latest_year = q3b["year"].max()
subset = q3b[q3b["year"] == latest_year].sort_values("difference")

fig, ax = plt.subplots(figsize=(8, 5))
colors = ["red" if d < 0 else "blue" for d in subset["difference"]]

ax.barh(subset["age_group"], subset["difference"], color=colors, alpha=0.85)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title(f"Participation Rate Difference by Age Group ({latest_year})\nUSA minus Germany")
ax.set_xlabel("Difference (percentage points)")
ax.set_ylabel("Age Group")
ax.grid(True, alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q3b_age_diff.png", dpi=150)
plt.show()

conn.close()