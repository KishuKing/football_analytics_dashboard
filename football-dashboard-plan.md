# Football Player Performance Analytics Dashboard — Implementation Plan

## Top-Level Overview

**Goal:** Build a self-contained, portfolio-quality interactive football (soccer) analytics
dashboard in Python + Streamlit that lets users explore, filter, compare, and download
synthetic player performance data across four pages.

**Scope:**
- Four deliverable files: `app.py`, `football_players.csv`, `requirements.txt`, `README.md`
- Fully synthetic dataset (100+ players, clearly labelled)
- Dark, football-inspired UI via Streamlit theming and custom CSS
- Zero external API calls — all data is local

**Non-goals:**
- Real-world scraping or external data feeds
- User authentication or persistent state
- Deployment infrastructure (only instructions are required)

---

## Dataset Schema

File: `football_players.csv`

| Column            | Type    | Description                                   |
|-------------------|---------|-----------------------------------------------|
| `player_id`       | int     | Unique identifier (1–N)                       |
| `player_name`     | str     | Synthetic full name                           |
| `team`            | str     | Club name (8 synthetic clubs)                 |
| `position`        | str     | GK / DEF / MID / FWD                          |
| `season`          | str     | "2022-23" or "2023-24"                        |
| `age`             | int     | 18–36                                         |
| `appearances`     | int     | 1–38                                          |
| `goals`           | int     | Position-appropriate range                    |
| `assists`         | int     | Position-appropriate range                    |
| `shots`           | int     | Position-appropriate range                    |
| `shots_on_target` | int     | ≤ shots                                       |
| `passes`          | int     | 10–120 per game × appearances                 |
| `key_passes`      | int     | ≤ passes / 10                                 |
| `tackles`         | int     | Position-appropriate range                    |
| `interceptions`   | int     | Position-appropriate range                    |
| `yellow_cards`    | int     | 0–10                                          |
| `red_cards`       | int     | 0–2                                           |
| `minutes_played`  | int     | appearances × 60–90                           |
| `rating`          | float   | 5.0–9.5, one decimal place                    |
| `clean_sheets`    | int     | GK-focused (0 for outfield)                   |
| `saves`           | int     | GK-focused (0 for outfield)                   |

**Generation rules:**
- Use `numpy.random.seed(42)` for full reproducibility
- Position-based stat distributions (GKs get high saves/clean_sheets, FWDs get high goals/shots)
- A visible `NOTE` column value of `"Synthetic data — not real football statistics"` on every row
  is NOT needed; the label is surfaced in the UI banner instead

---

## KPI Calculations (Overview Page)

All computed at runtime from the filtered DataFrame:

| KPI Card              | Formula                                      |
|-----------------------|----------------------------------------------|
| Total Players         | `df['player_id'].nunique()`                  |
| Total Goals           | `df['goals'].sum()`                          |
| Total Assists         | `df['assists'].sum()`                        |
| Total Minutes Played  | `df['minutes_played'].sum()`                 |
| Average Player Rating | `df['rating'].mean()` rounded to 2 dp        |

---

## Chart Choices

| Page             | Chart                              | Library              | Reason                                          |
|------------------|------------------------------------|----------------------|-------------------------------------------------|
| Overview         | KPI metric cards                   | Streamlit `metric()` | Instant at-a-glance numbers                     |
| Player Analysis  | Goals vs Assists scatter           | Plotly Express       | Reveals outlier contributors; color = position  |
| Player Analysis  | Shots vs Goals scatter             | Plotly Express       | Shows conversion efficiency; size = appearances |
| Player Analysis  | Radar / bar for player comparison  | Plotly Graph Objects | Multi-stat comparison of up to 3 players        |
| Team Analysis    | Grouped bar — goals & assists      | Plotly Express       | Side-by-side team comparison                    |
| Team Analysis    | Bar — player count per team        | Plotly Express       | Squad depth overview                            |
| Position Analysis| Box plot — rating by position      | Plotly Express       | Distribution across positions                   |
| Position Analysis| Stacked bar — goals by position    | Plotly Express       | Aggregate contribution per role                 |

All charts use a consistent dark theme (`template="plotly_dark"`) with a subtle green accent
(`#00ff87`) matching the pitch-inspired colour scheme.

---

## Project Structure

```
football_analytics_dashboard/
├── app.py                  # Single-file Streamlit application
├── football_players.csv    # Synthetic dataset
├── requirements.txt        # Pinned dependencies
└── README.md               # Setup, run, and deploy instructions
```

`app.py` internal structure (logical sections, not separate files):

```
1. Imports & page config
2. CSS injection (dark theme + green accents)
3. Data loading & caching (@st.cache_data)
4. Synthetic data generator (called once if CSV missing)
5. Sidebar filters (season, team, position, player)
6. Filter application + validation / empty-state guard
7. Page router (Overview | Player Analysis | Team Analysis | Position Analysis)
8. Each page as a named function: page_overview(), page_player(), page_team(), page_position()
9. CSV download button (shared footer utility)
```

---

## Sub-Tasks

---

### Sub-Task 1 — Generate Synthetic Dataset

**Intent:** Create `football_players.csv` with reproducible, realistic-looking data that
covers all positions, two seasons, and multiple clubs. This file is the single source of
truth for every chart and KPI.

**Expected Outcomes:**
- `football_players.csv` exists with ≥ 100 rows and all 21 columns defined in the schema
- Running the generator again with the same seed produces byte-identical output
- No NaN values in any column

**Todo List:**
1. Write a standalone Python script (or function inside `app.py`) using `numpy.random.seed(42)`
2. Define 8 synthetic team names and position distribution (GK 8%, DEF 28%, MID 36%, FWD 28%)
3. Generate per-position stat ranges using `numpy.random.randint` / `numpy.random.uniform`
4. Ensure `shots_on_target ≤ shots`, `key_passes ≤ passes // 5`, `minutes_played` derived from appearances
5. Save to CSV with `index=False`

**Relevant Context:** No existing files. Use `pandas.DataFrame` + `numpy` only.

**Status:** `[ ] pending`

---

### Sub-Task 2 — Streamlit App Skeleton & Theme

**Intent:** Establish `app.py` with page configuration, dark CSS, sidebar navigation, and the
data-loading/caching layer before any page content is written.

**Expected Outcomes:**
- `streamlit run app.py` launches without errors
- Dark background, green accent colour `#00ff87` visible in header and sidebar
- Sidebar shows navigation radio buttons: Overview, Player Analysis, Team Analysis, Position Analysis
- A yellow synthetic-data banner appears at the top of every page
- Data loads from CSV via `@st.cache_data`; if CSV is absent, the generator is called first

**Todo List:**
1. Set `st.set_page_config(layout="wide", page_title=..., page_icon="⚽")` as the first Streamlit call
2. Inject CSS via `st.markdown(unsafe_allow_html=True)` — dark background `#0e1117`, card styles, green highlights
3. Add `@st.cache_data` data-loader function that reads `football_players.csv`
4. Build sidebar: logo emoji, app title, navigation radio, then filter widgets (season, team, position, player multi-select)
5. Add an `st.info()` synthetic-data disclaimer banner

**Relevant Context:** Sub-Task 1 must be complete so the CSV exists when the app first loads.

**Status:** `[ ] pending`

---

### Sub-Task 3 — Sidebar Filters & Validation

**Intent:** Wire the sidebar filter widgets to the loaded DataFrame and add robust
input validation so that no downstream page receives an empty or invalid slice.

**Expected Outcomes:**
- Selecting any combination of season / team / position / player correctly narrows `df_filtered`
- When filters produce zero rows, a friendly `st.warning()` message is shown and pages do not crash
- Player multi-select is populated dynamically from the currently filtered team/position slice

**Todo List:**
1. Apply filters sequentially: season → team → position → player
2. Add a `validate_filters(df)` guard: if `len(df) == 0` show warning and `st.stop()`
3. Ensure "All" / empty selection means no filter applied for each dimension
4. Add a **Reset Filters** button that clears session state selections

**Relevant Context:** Filter logic lives between data load and the page router in `app.py`.

**Status:** `[ ] pending`

---

### Sub-Task 4 — Overview Page

**Intent:** Build the landing page with five KPI metric cards and a top-10 players leaderboard
table so users get an instant summary of the filtered data.

**Expected Outcomes:**
- Five `st.metric()` cards in one row: Total Players, Total Goals, Total Assists, Total Minutes, Avg Rating
- A ranked top-10 players table (sorted by goals desc, then assists desc) rendered with `st.dataframe()`
- All values computed from `df_filtered` — changing filters updates cards in real time

**Todo List:**
1. Create `page_overview(df)` function
2. Compute the five KPIs from the DataFrame (no hardcoded values)
3. Lay out cards with `st.columns(5)`
4. Build the top-10 leaderboard by sorting and slicing `df_filtered`
5. Style the table (hide index, highlight goals column)

**Relevant Context:** KPI formulas defined in the Dataset Schema section above.

**Status:** `[ ] pending`

---

### Sub-Task 5 — Player Analysis Page

**Intent:** Provide player-level scatter plots for goals vs assists and shots vs goals, plus
a radar chart for comparing up to three selected players across key stats.

**Expected Outcomes:**
- Goals vs Assists scatter — points coloured by position, hover shows player name + team
- Shots vs Goals scatter — point size encodes appearances, hover shows conversion rate
- Player comparison widget: multi-select (max 3 players), radar chart with 6 normalised stats
- Charts use `plotly_dark` template and `#00ff87` accent

**Todo List:**
1. Create `page_player(df)` function
2. Add Goals vs Assists scatter using `px.scatter` with `color="position"`, `hover_data=["player_name","team"]`
3. Add a computed `conversion_rate` column (`goals/shots` where shots > 0, else 0) for the second scatter
4. Add Shots vs Goals scatter with `size="appearances"`
5. Add player comparison multi-select (limit enforced with `st.warning` if > 3)
6. Build radar chart using `go.Scatterpolar` with normalised stats (goals, assists, rating, tackles, passes, shots)

**Relevant Context:** Sub-Task 3 must be complete (filtered df available).

**Status:** `[ ] pending`

---

### Sub-Task 6 — Team Analysis Page

**Intent:** Aggregate player stats by team to show which clubs score most, create most assists,
and carry the largest squads.

**Expected Outcomes:**
- Grouped bar chart: total goals and assists per team, side by side
- Bar chart: player count per team
- Summary table of team aggregates with download option

**Todo List:**
1. Create `page_team(df)` function
2. Group `df_filtered` by `team`: sum goals, sum assists, count players
3. Plot grouped bar with `px.bar(..., barmode="group")`
4. Plot player count bar separately
5. Show aggregated team table with `st.dataframe()`

**Relevant Context:** Sub-Task 3 must be complete.

**Status:** `[ ] pending`

---

### Sub-Task 7 — Position Analysis Page

**Intent:** Break down performance by playing position to highlight role-specific contributions
(GK saves, DEF tackles, MID key passes, FWD goals).

**Expected Outcomes:**
- Box plot of `rating` by position (shows spread and median)
- Stacked bar of total goals and assists per position
- Position-specific callout stats: avg saves for GK, avg tackles for DEF, avg key_passes for MID, avg goals for FWD

**Todo List:**
1. Create `page_position(df)` function
2. Build rating box plot with `px.box(color="position")`
3. Build stacked goals/assists bar with `px.bar(barmode="stack")`
4. Compute per-position callout stats and display with `st.metric()` in a 4-column row

**Relevant Context:** Sub-Task 3 must be complete.

**Status:** `[ ] pending`

---

### Sub-Task 8 — Searchable Stats Table & CSV Download

**Intent:** Give users a full, searchable player statistics table with a CSV export button so
the dashboard is useful for detailed lookup as well as visual exploration.

**Expected Outcomes:**
- `st.dataframe()` with column sorting enabled, showing all columns of `df_filtered`
- A search text input above the table that filters rows by player name (case-insensitive substring)
- A `st.download_button()` that exports the current filtered+searched slice as CSV
- Available on every page via a shared utility function or as a dedicated "Data" section

**Todo List:**
1. Create `render_data_table(df)` utility function
2. Add `st.text_input("Search player...")` and apply `.str.contains()` filter
3. Render with `st.dataframe(use_container_width=True)`
4. Wire `st.download_button` with `df.to_csv(index=False).encode("utf-8")`

**Relevant Context:** Called from each page function or appended as a collapsible expander.

**Status:** `[ ] pending`

---

### Sub-Task 9 — Requirements & README

**Intent:** Produce `requirements.txt` and `README.md` so any developer can clone, install, run,
and optionally deploy the dashboard in minutes.

**Expected Outcomes:**
- `requirements.txt` lists exact packages: `streamlit`, `pandas`, `numpy`, `plotly`
- `README.md` contains: project description, screenshot placeholder, setup steps, run command,
  Streamlit Cloud deploy instructions, dataset description, and licence note

**Todo List:**
1. Write `requirements.txt` with four dependencies (no version pins that would cause conflicts)
2. Write `README.md` with sections: Overview, Features, Installation, Usage, Dataset, Deploy, Licence

**Relevant Context:** No existing files.

**Status:** `[ ] pending`

---

## Implementation Order

```
Sub-Task 1 (CSV) → Sub-Task 2 (Skeleton) → Sub-Task 3 (Filters)
    → Sub-Tasks 4–7 (Pages, parallelisable in principle but sequential here)
        → Sub-Task 8 (Table/Download) → Sub-Task 9 (Docs)
```
