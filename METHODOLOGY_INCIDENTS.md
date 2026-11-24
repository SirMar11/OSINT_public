# Methodology – Incident Research (RQ3, RQ4)

RQ1 and RQ2 are answered from satellite catalogues. RQ3 and RQ4 are answered mainly by
**structured desk research** of public sources, supported by our own orbital data where possible.
This document fixes the rules *before* the research starts, so that the list of incidents does not
depend on what we happened to find.

- **RQ3:** Were there any documented attacks on satellites between 2021 and 2026, and what were their consequences?
- **RQ4:** Which space incidents between 2021 and 2026 increased tension between the USA and Russia?

## 1. Scope

| | Rule |
|---|---|
| Period | RQ4: events from **1 Jan 2021 to 30 Sep 2026** (same end as RQ1/RQ2); RQ3 follows Section 4.3 of the team report and also includes the Oct 2026 approach of Kosmos 2612 (date of the event, or of its first public disclosure if the event date is unknown) |
| Actors | the USA and Russia: governments, armed forces, and companies registered in either country |
| Space systems | satellites, their ground segment (stations, user terminals) and their radio links; ground radars and antennas that do not control satellites (e.g. space surveillance radars) are not included (team decision) |
| Languages | English and Russian |

**Team decision:** RQ3 asks about attacks on satellites in general. We limit it to attacks
**by or against US or Russian actors**, to stay within the topic of the project (see Limitations).

## 2. Definitions

### 2.1 Incident (RQ4)
An event is an **incident that increased US–Russia tension** if it meets **both** conditions:

1. **Action:** one country (its government, armed forces or a company acting for it) did something
   that affected, threatened or targeted a space system of the other country, or changed the rules
   between the two countries in space (e.g. a veto, a treaty step, a weapons disclosure); and
2. **Official reaction:** the other country's government reacted publicly – a statement, a formal
   attribution, a diplomatic step, a UN vote or a sanction. An intelligence leak or media report
   without any official confirmation is **not enough**.

Condition 2 is what turns "something happened" into "tension increased" and makes the selection
checkable. Events that fail it stay in `data/incidents.csv` with `rq4 = no` and the reason, so that the
selection can be reviewed. While the official reaction is still being checked, the value is `pending`.

**Initiator.** The initiator of an incident is the country whose step triggered the other side's official reaction.
In UN cases this is the side whose proposal or veto was reacted to: a US proposal that Russia opposed counts as a US step,
a Russian veto that the USA reacted to counts as a Russian step. Norm-building steps (test moratorium, UN resolutions) are
included because they change the rules between the two countries, but they are named as such in the report.

### 2.2 Attack (RQ3)
An **attack** is a deliberate action that **destroyed, damaged, disrupted or denied** a space system.
A capability demonstration without effect (e.g. a close approach) is an incident, not an attack.
A destructive test on a country's own satellite counts as an attack, because it destroyed a satellite
and its debris endangered others.

The RQ3 table (as in Section 4.3 of the team report) lists attacks together with **counterspace activities**
(co-orbital approaches without effect) and gives each event an **evidence level**:

| Level | Meaning |
|---|---|
| Confirmed | admitted by the actor, or formally attributed by several governments with supporting technical data |
| Attributed | named by a government without public technical evidence |
| Claimed or suspected | reported only by the victim, the media or a hacker group |

### 2.3 Incident types
Each incident gets exactly **one** type. The types follow the counterspace categories of the
Secure World Foundation (*Global Counterspace Capabilities*) and CSIS (*Space Threat Assessment*),
plus one political category:

| Type | Includes | Decision rule if several apply |
|---|---|---|
| Direct-ascent ASAT | missile from Earth destroying a satellite | always wins |
| Co-orbital | satellite manoeuvring close to, or placed into the orbit of, another country's satellite | wins over disclosure |
| Electronic warfare | jamming, spoofing | |
| Cyber | attack on satellite networks, ground segment or terminals | |
| Weapons disclosure | official statement revealing or confirming a counterspace weapon | used only if no physical event is described |
| Diplomacy and threats | UN votes and vetoes, official threats, withdrawal from cooperation | used only if nothing above applies |

**One event = one record.** Several reports about the same launch or the same manoeuvre are merged
(e.g. a launch and a later close approach by satellites from that launch are one incident, with
both dates noted).

## 3. Sources

Sources are used in four tiers. Every incident needs **at least two independent sources**, at least
one of them from tier 1 or 2.

| Tier | Sources | Used for |
|---|---|---|
| 1 – Official | US: White House, State Dept., DoD, US Space Command, Space Force; Russia: MID, Ministry of Defence, Roscosmos; UN records (Security Council, General Assembly First Committee, OEWG on space threats); EU and NATO attributions | that an event happened and how a government reacted |
| 2 – Expert and data | Secure World Foundation *Global Counterspace Capabilities* (annual), CSIS *Space Threat Assessment* (annual), J. McDowell (GCAT, Jonathan's Space Report), A. Zak (RussianSpaceWeb), Space-Track.org | technical facts, orbits, timelines |
| 3 – Specialised press | SpaceNews, Breaking Defense, SpacePolicyOnline, Ars Technica, The Record | details, quotes, context |
| 4 – General press | Reuters, AP, AFP, BBC | first reports, reactions |

Russian state media (TASS, RIA Novosti) are used **only to document the Russian official position**,
not as evidence of facts. The same applies to statements of any government about its own actions.

### 3.1 Reliability rating
Each incident is rated with the **Admiralty Code** (NATO): source reliability **A–F** and information credibility **1–6**.
The rating reflects the strongest evidence for the incident:

| Rating | Used when |
|---|---|
| A1 | UN records or official documents confirmed by both sides |
| B1 | official statement or attribution confirmed by independent sources or by our own data |
| B2 | official statement of one side supported by independent reporting or tracking |
| B3 | intelligence-based claim of one side that the other side denies |

Syndicated copies of the same agency report (e.g. AFP or Reuters republished by other outlets) do not count as independent sources.

## 4. Search procedure

1. **Seed list.** Go through the SWF and CSIS reports for 2022–2026 (each covers the previous year)
   and list every event involving the USA and Russia. These reports are compiled systematically, so the
   list does not depend on our own searching.
2. **Keyword search.** Search tier 1 and 3 sources for the period with fixed queries, in English and Russian:
   - `ASAT`, `anti-satellite`, `counterspace`, `co-orbital`, `inspector satellite`, `rendezvous proximity operations`
   - `satellite jamming`, `GPS jamming`, `Starlink jamming`, `satellite cyberattack`
   - `Kosmos` + `USA`, `Space Command` + `Russia`, `space weapon` + `Russia`
   - `противоспутниковое`, `спутник-инспектор`, `Космос` + `США`
3. **Snowballing.** Follow references in the sources found until no new events appear.
4. **Search log.** Every query is recorded in `data/search_log.csv` (date, source, query, number of
   hits, new events). This makes the search repeatable.
5. **Screening.** Each candidate is checked against the definitions in section 2 and goes either to
   RQ3 (`rq3 = yes`), RQ4 (`rq4 = yes`), both, or neither; the reason is recorded in `note`.

## 5. Verification with our own data

Co-orbital incidents name concrete satellites. For these we check in Space-Track data whether the
Russian satellite really shared the orbit of the US satellite: inclination, altitude and orbital plane
(right ascension of the ascending node) over time, from the historical orbital elements (GP history).
Each case is marked **confirmed**, **not confirmed** or **cannot be checked** (e.g. the US satellite
has no published orbit). The check is done by `src/05_incidents.py`.

## 6. Recording

Incidents are recorded in **`data/incidents.csv`**, one row per incident:

| Column | Content |
|---|---|
| `id` | running number |
| `rq3` | `yes`/`no`/`pending`: `yes` if the event is an attack by section 2.2 and within the RQ3 scope |
| `rq4` | `yes`/`no`/`pending` by section 2.1 (`pending` = official reaction not yet verified) |
| `note` | reason for `no`/`pending`, merged events, open questions |
| `date`, `date_disclosed` | date of the event; date of first public disclosure if different |
| `type` | one type from section 2.3 |
| `actor`, `target` | country and system (e.g. `RU / Kosmos 2576`, `US / USA 314`) |
| `description` | what happened, one or two sentences |
| `reaction` | official reaction of the other government |
| `consequences` | for attacks: physical, operational and political consequences |
| `ru_norad`, `us_norad` | NORAD numbers for co-orbital incidents |
| `orbit_check` | result of section 5 |
| `sources` | short citations; full references in the report |
| `reliability` | Admiralty rating, e.g. `B2` |

Table and figure for the report are generated from this file by `src/05_incidents.py`.

## 7. Analysis

- **RQ4:** number of incidents by type and year; timeline (Figure 5); whether incidents moved from
  tests and threats towards deployed weapons. Targets are linked to our satellite data: mission type
  (Table 3) and orbit regime (Table 4) of the targeted satellites.
- **RQ3:** for each attack, consequences in three dimensions:
  - **physical** – destroyed objects, debris (for Kosmos 1408 our own debris data, Table 5b in FINDINGS),
  - **operational** – outages, affected users and duration,
  - **political** – attribution, sanctions, UN steps, new commitments (e.g. the US moratorium on destructive ASAT tests).

## 8. Limitations

- **Classified activity.** Only what governments, companies or analysts made public can be found.
  The list is a lower bound.
- **English-language search.** Searches were in English, so Russian reactions to US steps are harder to find; this biases the
  count of initiators towards Russia. Russian-language sources (MID, TASS in Russian) would reduce the bias.
- **Amateur orbital data not used.** Orbits of classified US satellites published by amateur observers (e.g. SeeSat-L) could verify
  co-orbital incidents that Space-Track cannot.
- **Western source bias.** Most tier 1–3 sources are American or European. Russian official sources
  are included, but Russia rarely discloses its own operations.
- **Disclosure lag.** Some events become public months later. We record both dates.
- **Scope.** Only attacks by or against US or Russian actors are covered (e.g. not attacks between other countries).
- **Cut-off.** Events after 30 Sep 2026 and events disclosed after our search date are not included.
