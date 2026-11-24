# USA vs Russia Satellite Tracking

Data analysis for the semester project in *Open Source Intelligence* (4IT556, VŠE).
The analysis plan is in [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md).

## Setup

Requires Python 3.12+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then fill in your Space-Track credentials
```

The GCAT catalogs are downloaded manually (no login needed):

```powershell
mkdir data\raw\gcat
curl.exe -o data\raw\gcat\psatcat_YYYY-MM-DD.tsv https://planet4589.org/space/gcat/tsv/cat/psatcat.tsv
curl.exe -o data\raw\gcat\satcat_YYYY-MM-DD.tsv https://planet4589.org/space/gcat/tsv/cat/satcat.tsv
```

## Run

Run the scripts in order from the project root:

| Script | What it does | Output |
|---|---|---|
| `src/01_download.py` | downloads US and Russian payloads from Space-Track SATCAT (+ ISS-deployed payloads) | `data/raw/satcat_<date>.csv`, `data/raw/iss_deployed_<date>.csv` |
| `src/02_classify.py` | adds launch id, category (military / civil / commercial / Starlink) and orbit regime | `data/processed/satellites_classified.csv` |
| `src/03_charts.py` | RQ1/RQ2 tables and charts, evaluates H1 on Space-Track and GCAT orbits | `output/tables/rq1_*, rq2_*`, `output/figures/fig1–3` |
| `src/04_debris.py` | RQ3: Kosmos 1408 debris on orbit over time | `output/tables/rq3_debris.csv`, `output/figures/fig4_debris.png` |
| `src/05_incidents.py` | RQ4: incident timeline and counts from `data/incidents.csv`; orbital-plane check of co-orbital incidents (needs `.env`) | `output/tables/rq4_*.csv`, `output/figures/fig5_incidents.png` |

Figure files vs. figure numbers in the team report and `report/`: `fig1_quarterly` = Figure 1, `fig4_debris` = Figure 2,
`fig5_incidents` = Figure 3, `fig3_scatter` = Figure A1 (`fig2_orbits` is not used in the report).

Downloads run only once per day (if today's file exists, Space-Track is not contacted).

## Data sources

- **Space-Track.org** SATCAT (account required), retrieved **2026-11-18**.
- **GCAT** by Jonathan McDowell (planet4589.org), `psatcat.tsv` and `satcat.tsv`, version updated 2026-11-18.
  Used to classify satellites whose name does not reveal the operator, to date ISS-deployed satellites,
  and as an **independent second source of orbit regime** (`OpOrbit`) for testing H1.
- **Incidents (RQ3/RQ4):** SWF *Global Counterspace Capabilities* 2026, CSIS *Space Threat Assessment* 2022–2025,
  official statements and news, compiled by hand in `data/incidents.csv` (queries in `data/search_log.csv`).
- Raw and processed data are committed in `data/` so the team can work without downloading.
  Space-Track terms do not allow redistribution, so **this public copy contains no Space-Track data**; run `src/01_download.py` with your own account to recreate it.
  The public report contains only aggregated tables and charts from `output/`.

## Method in brief

Full description of satellite classification systems and our mapping: [METHODOLOGY.md](METHODOLOGY.md).
Rules for the incident research (RQ3/RQ4): [METHODOLOGY_INCIDENTS.md](METHODOLOGY_INCIDENTS.md).

- **Study period:** launches from 2022-02-24 (start of the Russian invasion of Ukraine) to 2026-09-30.
  Payloads only; decayed satellites are included. Russia = Space-Track country code `CIS`.
- **ISS-deployed satellites:** Space-Track gives them the ISS designator and launch date (1998-067, 1998-11-20).
  They are added separately; launch date and launch id are taken from their cargo flight (GCAT `LDate`, `Launch_Tag`).
  Objects GCAT does not list as payloads (items jettisoned during spacewalks) are dropped. 26 satellites added (21 US, 5 Russia).
- **Orbital launches** = distinct launches (international designator `YYYY-NNN`) carrying at least
  one payload of the country, regardless of the rocket's country.
- **Category**, first match wins:
  1. name rules (`STARLINK` → Starlink, `USA xxx` / `PRAETORIAN SDA` / `COSMOS` → military, a few named commercial and civil series),
  2. GCAT `Class` (D → military, C/A → civil, B → commercial),
  3. otherwise unknown; `manual_overrides.csv` overrides everything.
  GLONASS (COSMOS with GCAT category NAV) is counted as military (`GLONASS_CATEGORY` in `02_classify.py`).
  Name rules agree with GCAT in 10 746 of 10 747 cases.
- **Orbit regime** from apogee, perigee and period: LEO (apogee < 2 000 km), HEO (eccentricity > 0.25),
  GEO (period 1 400–1 460 min, e < 0.05), otherwise MEO; unknown if orbital data are missing
  (deep-space missions and 7 US military satellites without published orbits).
  The regime is based on the current or last known orbit, not the orbit at launch.
- **H1 test:** LEO share = LEO / all payloads in the group (unknown orbits included, conservative).
  Confirmed if USA excl. Starlink, Russia, US military and Russian military are all above 50 %;
  partially confirmed if only some are; rejected if none.
  Tested twice: on Space-Track orbits and on GCAT `OpOrbit`. H1 is verified only if both sources agree
  (`rq2_orbits_gcat.csv`, `rq2_source_comparison.csv`).
- **Limitation:** GCAT does not yet contain objects launched after ~11 July 2026 (new 6-digit NORAD numbers);
  these were classified by name rules only, have no mission type, and GLONASS satellites among them would not be
  recognised (no effect now, COSMOS is military either way).

## Main results (retrieved 2026-11-18)

**RQ1 – payloads launched 2022-02-24 to 2026-09-30**

|  | USA | USA excl. Starlink | Russia |
|---|---|---|---|
| Orbital launches | 588 | 209 | 84 |
| Payloads total | 12 533 | 1 720 | 185 |
| Military | 514 | 514 | 71 |
| Civil | 99 | 99 | 63 |
| Commercial | 1 095 | 1 095 | 49 |
| Starlink | 10 813 | – | – |
| Unknown | 12 | 12 | 2 |

**RQ2 – H1 (both countries focus on LEO): confirmed, also for military satellites.**
LEO share: USA 99.2 %, USA excl. Starlink 94.4 %, Russia 88.1 %, US military 90.5 %, Russian military 80.3 %.
Verified with GCAT as a second source (lowest share 70 %, US military). Where both sources know the orbit, they disagree on ~0.1 % of payloads.

**RQ3 – Documented attacks and counterspace activities (2021–2026, as in Section 4.3 of the team report):**
9 events, each with an evidence level (confirmed / attributed / claimed). The only destructive one was Russia's Kosmos 1408
ASAT test (2021-11-15): 1 806 catalogued debris pieces (designator 1982-092); about half had decayed by mid-2022 and 4 remained
on orbit on 2026-11-04. All hostile actions against other countries were non-destructive: cyberattacks (Viasat KA-SAT,
Dozor-Teleport), jamming (GPS, Starlink, TV broadcasting satellites, UK and German military satellites) and close approaches
of Russian satellites to US reconnaissance satellites and to ICEYE-X36.

**RQ4 – US–Russia space incidents (Nov 2021 – Sep 2026):** 12 of 28 screened candidates meet both criteria
(an action toward the other country's space systems and an official reaction of the other government).
Russia initiated 9 of them. The most common types were co-orbital approaches to US imaging satellites (4) and
diplomacy and threats (4). Tension moved from a destructive test and threats (2021–2022) to the acknowledgement of US space weapons and US
accusations of Russian ones, which Russia denies (2024–2026). Russian jamming of Starlink and GPS drew no official US protest and is therefore not counted.
