"""Step 5 (RQ3/RQ4) - incident timeline and orbit check of co-orbital incidents.

Input:   data/incidents.csv  (hand-curated, see METHODOLOGY_INCIDENTS.md)
Output:  output/tables/rq4_counts.csv       - RQ4 incidents by type and year
         output/tables/rq4_orbit_check.csv  - orbital plane check (needs Space-Track login)
         output/figures/fig5_incidents.png  - timeline of RQ4 incidents

Timeline date = event date; for weapons disclosures the disclosure date,
because the disclosure itself is the event (e.g. Kosmos 2553 launched in 2022,
disclosed in 2024).

Orbit check (METHODOLOGY_INCIDENTS.md, section 5): for each co-orbital incident
with both NORAD numbers, the orbital elements history (GP history) of the
Russian and the US satellite is downloaded for 90 days after the event. For each
Russian element set the nearest US one is taken and the angle between the two
orbital planes is computed from inclination and RAAN. Median angle below
PLANE_LIMIT = confirmed co-planar.

Usage (from project root):  python src/05_incidents.py
"""

import io
import math

import matplotlib

matplotlib.use("Agg")   # draw to files only, no window
import matplotlib.pyplot as plt
import pandas as pd

from common import DATA_RAW, FIGURES, ROOT, TABLES, spacetrack_query

INCIDENTS = ROOT / "data" / "incidents.csv"
DPI = 300
CHECK_DAYS = 90       # length of the orbit-check window after the event
PLANE_LIMIT = 1.0     # degrees; median plane angle below this = co-planar

# Rows of the timeline, top to bottom (types from METHODOLOGY_INCIDENTS.md 2.3)
TYPES = ["Direct-ascent ASAT", "Cyber", "Electronic warfare", "Co-orbital",
         "Weapons disclosure", "Diplomacy and threats"]
MARKERS = {"Direct-ascent ASAT": "X", "Cyber": "s", "Electronic warfare": "P",
           "Co-orbital": "o", "Weapons disclosure": "D", "Diplomacy and threats": "^"}


def load():
    df = pd.read_csv(INCIDENTS, dtype=str).fillna("")
    rq4 = df[df["rq4"] == "yes"].copy()
    # Weapons disclosures are dated by the disclosure, the rest by the event
    use_disclosed = (rq4["type"] == "Weapons disclosure") & (rq4["date_disclosed"] != "")
    rq4["plot_date"] = pd.to_datetime(rq4["date"].where(~use_disclosed, rq4["date_disclosed"]))
    print(f"Incidents in file: {len(df)}, RQ4 incidents: {len(rq4)}, RQ3 attacks: {(df['rq3'] == 'yes').sum()}")
    return rq4


def counts_table(rq4):
    """RQ4 incidents by type (rows) and year (columns)."""
    table = pd.crosstab(rq4["type"], rq4["plot_date"].dt.year)
    # all types and years, zeros included, so that gaps are visible
    table = table.reindex(index=TYPES, columns=range(2021, 2027), fill_value=0)
    table["Total"] = table.sum(axis=1)
    table.loc["Total"] = table.sum()
    TABLES.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES / "rq4_counts.csv")
    print("\nRQ4 incidents by type and year:")
    print(table.to_string())


def fig5_timeline(rq4):
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    types = [t for t in TYPES if t in set(rq4["type"])]   # only rows that have an incident
    y = {t: len(types) - i for i, t in enumerate(types)}
    for _, r in rq4.iterrows():
        yy = y[r["type"]]
        ax.scatter(r["plot_date"], yy, marker=MARKERS[r["type"]], s=45, color="#333333", zorder=3)
        ax.annotate(r["id"], (r["plot_date"], yy), xytext=(0, 7), textcoords="offset points",
                    ha="center", fontsize=7, fontweight="bold")
    ax.set_yticks(list(y.values()), list(y.keys()))
    ax.set_ylim(0.4, len(types) + 0.7)
    ax.set_xlim(pd.Timestamp("2021-07-01"), pd.Timestamp("2026-12-31"))
    ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.set_title("US-Russia space incidents, Nov 2021 - Sep 2026", loc="left", fontweight="bold", fontsize=9)
    fig.text(0.01, 0.01, "Numbers = id in data/incidents.csv. Source: SWF, CSIS, official statements and news "
             "(see incident table); own compilation.", fontsize=6.5, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "fig5_incidents.png", dpi=DPI)
    plt.close(fig)


def plane_angle(i1, raan1, i2, raan2):
    """Angle between two orbital planes in degrees (from inclinations and RAANs)."""
    i1, i2, d = map(math.radians, (i1, i2, raan1 - raan2))
    c = math.cos(i1) * math.cos(i2) + math.sin(i1) * math.sin(i2) * math.cos(d)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def gp_history(ru, us, start):
    """Element sets of both satellites for CHECK_DAYS after start (downloaded once)."""
    raw_file = DATA_RAW / f"gp_history_{ru}_{us}_{start.date()}.csv"
    if not raw_file.exists():
        end = (start + pd.Timedelta(days=CHECK_DAYS)).date()
        query = (f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{ru},{us}"
                 f"/EPOCH/{start.date()}--{end}/orderby/EPOCH asc/format/csv")
        raw_file.write_text(spacetrack_query(query), encoding="utf-8")
    text = raw_file.read_text(encoding="utf-8")
    return pd.read_csv(io.StringIO(text)) if text.strip() else pd.DataFrame()


def orbit_check(incidents):
    """Orbital-plane check of co-orbital incidents with both NORAD numbers."""
    co = incidents[(incidents["type"] == "Co-orbital") & (incidents["rq4"] == "yes")]
    if not (ROOT / ".env").exists():
        print(f"\nOrbit check skipped: no .env with Space-Track login ({len(co)} co-orbital incidents waiting).")
        return
    results = []
    for _, r in co.iterrows():
        row = {"id": r["id"], "ru_norad": r["ru_norad"], "us_norad": r["us_norad"]}
        if not (r["ru_norad"] and r["us_norad"]):
            results.append(row | {"result": "cannot be checked (NORAD number missing)"})
            continue
        gp = gp_history(r["ru_norad"], r["us_norad"], pd.Timestamp(r["date"]))
        sats = {n: gp[gp["NORAD_CAT_ID"].astype(str) == n] if len(gp) else gp for n in (r["ru_norad"], r["us_norad"])}
        ru, us = (sats[r["ru_norad"]], sats[r["us_norad"]])
        if ru.empty or us.empty:
            missing = " and ".join(side for side, s in (("RU", ru), ("US", us)) if s.empty)
            results.append(row | {"result": f"cannot be checked (no published elements for {missing} satellite)"})
            continue
        for s in (ru, us):
            s["EPOCH"] = pd.to_datetime(s["EPOCH"])
        pairs = pd.merge_asof(ru.sort_values("EPOCH"), us.sort_values("EPOCH"), on="EPOCH",
                              suffixes=("_ru", "_us"), direction="nearest", tolerance=pd.Timedelta(days=1)).dropna(
            subset=["INCLINATION_us"])
        angles = [plane_angle(p.INCLINATION_ru, p.RA_OF_ASC_NODE_ru, p.INCLINATION_us, p.RA_OF_ASC_NODE_us)
                  for p in pairs.itertuples()]
        if not angles:
            results.append(row | {"result": "cannot be checked (no element sets within 1 day of each other)"})
            continue
        median = pd.Series(angles).median()
        results.append(row | {"pairs": len(angles), "median_plane_angle_deg": round(median, 2),
                              "min_plane_angle_deg": round(min(angles), 2),
                              "result": "confirmed" if median < PLANE_LIMIT else "not confirmed"})
    table = pd.DataFrame(results)
    table.to_csv(TABLES / "rq4_orbit_check.csv", index=False)
    print("\nOrbit check (copy results to column orbit_check in data/incidents.csv):")
    print(table.to_string(index=False))


def main():
    incidents = pd.read_csv(INCIDENTS, dtype=str).fillna("")
    rq4 = load()
    counts_table(rq4)
    fig5_timeline(rq4)
    orbit_check(incidents)
    print(f"\nSaved {TABLES / 'rq4_counts.csv'} and {FIGURES / 'fig5_incidents.png'}")


if __name__ == "__main__":
    main()
