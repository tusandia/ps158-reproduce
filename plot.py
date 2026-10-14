"""Plot the college / high-school-or-less net worth gap from the SCF, 1989-2025.

Reads data/networth_by_education.csv (made by get_data.py) and writes
figures/networth_gap_by_education.png.

Left panel: median family net worth for the two groups. Right panel: the ratio
of the college median to the high-school-or-less median.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).parent
IN_FILE = ROOT / "data" / "networth_by_education.csv"
OUT_FILE = ROOT / "figures" / "networth_gap_by_education.png"

COLLEGE = "Bachelor's degree or more"
HS = "High school or less"

INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
SERIES = {COLLEGE: "#2a78d6", HS: "#eb6834"}
LABELS = {COLLEGE: "Bachelor's degree or more", HS: "High school or less"}


def main():
    df = pd.read_csv(IN_FILE)
    dollar_year = int(df["dollar_year"].iloc[0])
    wide = df.pivot(index="year", columns="group", values="median_networth") / 1e3
    ratio = wide[COLLEGE] / wide[HS]
    years = wide.index.to_numpy()

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK_2,
            "xtick.color": INK_2,
            "ytick.color": INK_2,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)

    for group, color in SERIES.items():
        ax1.plot(years, wide[group], color=color, lw=2, marker="o", ms=5,
                 markeredgecolor="white", markeredgewidth=1.5, label=LABELS[group])
        last = wide[group].iloc[-1]
        ax1.annotate(f"${last:,.0f}K", (years[-1], last), xytext=(6, 0),
                     textcoords="offset points", va="center", color=INK, fontsize=9)
    ax1.set_title(f"Median family net worth\nthousands of {dollar_year} dollars",
                  loc="left", color=INK, fontsize=11)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}K"))
    ax1.set_ylim(0, None)
    ax1.legend(frameon=False, loc="upper left", labelcolor=INK)

    ax2.plot(years, ratio, color=INK, lw=2, marker="o", ms=5,
             markeredgecolor="white", markeredgewidth=1.5)
    for y in (years[0], years[-1]):
        ax2.annotate(f"{ratio[y]:.1f}x", (y, ratio[y]), xytext=(0, 9),
                     textcoords="offset points", ha="center", color=INK, fontsize=9)
    ax2.set_title("Ratio: college median / high-school-or-less median",
                  loc="left", color=INK, fontsize=11)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}x"))
    ax2.set_ylim(0, ratio.max() * 1.2)

    for ax in (ax1, ax2):
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) if i % 2 == 0 else "" for i, y in enumerate(years)])
        ax.set_xlim(years[0] - 1.5, years[-1] + 3)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)

    fig.suptitle("The wealth gap between college-educated and high-school-educated families",
                 x=0.01, ha="left", color=INK, fontsize=13, fontweight="bold")
    fig.text(0.01, -0.03,
             "Education of the family's reference person. Source: Federal Reserve Board, "
             "Survey of Consumer Finances summary extracts, 1989-2025.",
             color=INK_2, fontsize=8)

    OUT_FILE.parent.mkdir(exist_ok=True)
    fig.savefig(OUT_FILE, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
