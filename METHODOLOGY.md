# Methodology – Satellite Classification

This document describes how satellites can be classified from open sources (RQ1) and how
orbits were verified with two independent sources (RQ2). Code references point to `src/`.

## 1. Classification systems in open sources

No single official classification of satellites exists. Open-source catalogues describe a satellite
along several independent dimensions:

### 1.1 Identifiers
| Identifier | Example | Assigned by |
|---|---|---|
| NORAD catalog number (SATCAT number) | `54247` | US Space Force (18th/19th Space Defense Squadron), published on Space-Track.org |
| COSPAR international designator | `2022-150A` = 150th launch of 2022, object A | COSPAR / UN registration practice |
| National designation | `USA 336`, `COSMOS 2558` | the operating state – the US uses `USA xxx` for government (mostly NRO/DoD) payloads, Russia uses `COSMOS xxxx` mainly for military payloads |

The international designator also identifies the **launch** (`YYYY-NNN`), which we use to count orbital launches.

### 1.2 By user / operator
| System | Values |
|---|---|
| UCS Satellite Database, field *Users* | Military, Government, Civil, Commercial (and combinations) |
| GCAT (J. McDowell), field *Class* | **A** academic, amateur and non-profit, **B** business/commercial, **C** civil government, **D** defense/military/intelligence; combinations such as `BD` for dual-use |

### 1.3 By mission
GCAT field *Category* gives the primary mission, e.g. `IMG` imaging/reconnaissance, `SIG` signals intelligence,
`COM` communications, `NAV` navigation, `EW` missile early warning, `TECH` technology demonstration.
The UCS database has an equivalent field *Purpose*.

### 1.4 By orbit
| Regime | Usual definition | Typical use |
|---|---|---|
| LEO – low Earth orbit | altitude below 2 000 km | imaging, broadband constellations, crewed flight |
| MEO – medium Earth orbit | between LEO and GEO (typically ~20 000 km) | navigation (GPS, GLONASS) |
| GEO – geostationary orbit | ~35 786 km, period ≈ 1 436 min, near-zero eccentricity and inclination | communications, early warning |
| HEO – highly elliptical orbit | strongly eccentric (e.g. Molniya, Tundra) | coverage of high northern latitudes |

The 2 000 km LEO limit matches the "LEO protected region" in the IADC Space Debris Mitigation Guidelines.
GCAT gives its own orbit class per object in the field *OpOrbit*: `LLEO` (mean height 80–600 km) and
`LEO` (600–2 000 km), `MEO`, `GEO` (period ≈ one sidereal day), `HEO` (eccentricity 0.50–0.92, incl. Molniya `HEO/M`),
`GTO`, `VHEO` (period > 25 h) and deep-space classes.

## 2. Our classification (how we map these systems)

We combine the systems above into five categories: **military, civil, commercial, Starlink, unknown**
(`src/02_classify.py`). The first match wins:

1. **Name rules.** The national designation reveals the operator, e.g. `USA xxx`, `PRAETORIAN SDA`, `COSMOS xxxx` → military; `STARLINK` → Starlink; `GLOBALSTAR`, `SPACEMOBILE`, `RASSVET` → commercial; `SOYUZ`, `PROGRESS` → civil.
2. **GCAT *Class*.** D (incl. combinations with D) → military, C and A → civil, B → commercial.
3. Otherwise **unknown**. Each such satellite is listed for manual review.
4. **Manual overrides** (`manual_overrides.csv`) win over everything.

Team decisions:
- **Starlink** is a separate category. It makes up ~86 % of US payloads and would otherwise hide all other trends.
- **GLONASS** (COSMOS with GCAT mission `NAV`) is counted as **military**. It is operated by the Russian Ministry of Defence, even though civil users use it too.
- Amateur/academic satellites (GCAT A) are counted as **civil**.

Military satellites are further split by mission using GCAT *Category* (Table 3 in `output/FINDINGS.md`).

**Orbit regime from Space-Track** (`orbit_regime()`), computed from apogee, perigee and period:
- LEO: apogee < 2 000 km
- HEO: eccentricity > 0.25
- GEO: period 1 400–1 460 min and eccentricity < 0.05
- MEO: the rest

## 3. Verification of orbits with two independent sources (RQ2)

Hypothesis H1 (majority of payloads in LEO) is tested on **two independent catalogues**:

| Source | Orbit determined from | Column |
|---|---|---|
| Space-Track.org SATCAT | apogee, perigee, period, with our thresholds above | `orbit` |
| GCAT (J. McDowell) | McDowell's own orbit class *OpOrbit* | `orbit_gcat` |

GCAT is compiled independently from Space-Track: it adds McDowell's own research, including objects
the US does not publish. *OpOrbit* is mapped by prefix: `LLEO`/`LEO` → LEO, `MEO` → MEO, `GEO` → GEO,
`HEO`/`VHEO`/`GTO` → HEO. H1 counts as verified only if it holds in **both** sources
(`src/03_charts.py`, tables `rq2_orbits.csv`, `rq2_orbits_gcat.csv` and `rq2_source_comparison.csv`).

The two sources use slightly different definitions: GCAT measures LEO by mean height and starts HEO at
eccentricity 0.50, while we use apogee and 0.25. The comparison therefore also tests how sensitive the result is to the definition.

### Limits
- 7 US military satellites (`USA xxx`) have no published orbital data on Space-Track.
- GCAT coverage ends around July 2026. Later launches have unknown orbit in GCAT, so the GCAT LEO share is a lower bound.
- Orbit is the current or last known orbit, not the orbit at launch.
