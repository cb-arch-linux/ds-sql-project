import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("labour_market.db")
COLORS = {"USA": "blue", "DEU": "red"}

q3a = pd.read_sql("""
    SELECT
        iso3,
        age_group,
        SUM(CASE WHEN year = 1995 THEN participation ELSE NULL END) AS y1995,
        SUM(CASE WHEN year = 2008 THEN participation ELSE NULL END) AS y2008,
        SUM(CASE WHEN year = 2019 THEN participation ELSE NULL END) AS y2019,
        SUM(CASE WHEN year = 2023 THEN participation ELSE NULL END) AS y2023
    FROM age_participation
    WHERE iso3 IN ('USA', 'DEU')
    GROUP BY iso3, age_group
    ORDER BY iso3, age_group
""", conn)

years = ["y1995", "y2008", "y2019", "y2023"]
year_labels = ["1995", "2008", "2019", "2023"]
age_groups = q3a["age_group"].unique()

fig, axes = plt.subplots(1, len(age_groups), figsize=(14, 6), sharey=True)
if len(age_groups) == 1:
    axes = [axes]

for ax, age in zip(axes, age_groups):
    subset = q3a[q3a["age_group"] == age]
    x = range(len(years))
    width = 0.35
    for i, (_, row) in enumerate(subset.iterrows()):
        offset = (i - 0.5) * width
        ax.bar([xi + offset for xi in x], row[years],
               width=width, label=row["iso3"], color=COLORS[row["iso3"]], alpha=0.85)
    ax.set_title(f"Age {age}")
    ax.set_xticks(list(x))
    ax.set_xticklabels(year_labels)
    ax.set_xlabel("Year")
    ax.grid(True, alpha=0.3, axis="y")

axes[0].set_ylabel("Participation Rate (%)")
handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[c]) for c in ["USA", "DEU"]]
fig.legend(handles, ["USA", "Germany"], loc="upper right")
fig.suptitle("Youth Participation Rate by Gender: USA vs Germany", fontsize=13)

plt.tight_layout()
plt.savefig("/Users/cameronbahlmann/git-projects/ds-sql-project-1/analysis/graphs/q3a_age_pivot.png", dpi=150)
plt.show()

conn.close()