# ⚽ Football Player Performance Analytics Dashboard

> **Synthetic Data Notice:** All player names, teams, and statistics in this dashboard are
> randomly generated for demonstration purposes only. They do **not** represent real football
> results or any real individuals.

A portfolio-quality interactive football (soccer) analytics dashboard built with
**Python**, **Streamlit**, and **Plotly**. Explore, compare, and download synthetic
player performance data across four analytical pages.

---

## 📸 Preview

```
⚽ Football Analytics Dashboard
├── Overview         — KPI cards, top-10 leaderboard, goals-by-position donut
├── Player Analysis  — Goals vs assists scatter, shots vs goals scatter, radar comparison
├── Team Analysis    — Grouped bar charts, squad size, avg rating per team
└── Position Analysis— Box plot, stacked bars, violin chart, position highlights
```

---

## ✨ Features

| Feature | Details |
|---|---|
| KPI Cards | Total players, goals, assists, minutes played, avg rating |
| Player Comparison | Radar chart comparing up to 3 players across 6 normalised stats |
| Scatter Plots | Goals vs assists (by position), shots vs goals (conversion rate) |
| Team Analysis | Grouped bar charts for goals/assists per team, squad size, avg rating |
| Position Analysis | Rating box plots, stacked goal/assist bars, position highlights |
| Sidebar Filters | Season, team, position, player (cascading, with reset button) |
| Searchable Table | Case-insensitive player name search on every page |
| CSV Download | Export filtered data as CSV from any page |
| Dark UI | Football-inspired dark theme with `#00ff87` green pitch accents |
| Input Validation | Empty-filter guard with friendly warning messages |

---

## 🚀 Installation & Local Run

### Prerequisites

- Python 3.10 or later
- pip

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/football-analytics-dashboard.git
cd football-analytics-dashboard

# 2. (Recommended) Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Pre-generate the dataset
python generate_data.py

# 5. Launch the dashboard
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.
Or Click this link: https://footballanalyticsdashboardibm.streamlit.app/

> If `football_players.csv` is missing when the app starts, it is generated automatically.

---

## 📂 Project Structure

```
football-analytics-dashboard/
├── app.py                    # Main Streamlit application (all pages)
├── generate_data.py          # Reproducible synthetic dataset generator
├── football_players.csv      # Pre-generated dataset (240 rows, 21 columns)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 📊 Dataset Schema

Generated with `numpy.random.seed(42)` — fully reproducible.

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique identifier |
| `player_name` | str | Synthetic full name |
| `team` | str | Club (8 synthetic clubs) |
| `position` | str | GK / DEF / MID / FWD |
| `season` | str | 2022-23 or 2023-24 |
| `age` | int | 18–36 |
| `appearances` | int | 1–38 |
| `goals` | int | Position-appropriate range |
| `assists` | int | Position-appropriate range |
| `shots` | int | Position-appropriate range |
| `shots_on_target` | int | ≤ shots |
| `passes` | int | Total passes |
| `key_passes` | int | ≤ passes / 5 |
| `tackles` | int | Position-appropriate range |
| `interceptions` | int | Position-appropriate range |
| `yellow_cards` | int | 0–10 |
| `red_cards` | int | 0–2 |
| `minutes_played` | int | Derived from appearances |
| `rating` | float | 5.0–9.5 |
| `clean_sheets` | int | GK-focused |
| `saves` | int | GK-focused |

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push the project to a **public GitHub repository**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → set **Main file path** to `app.py`.
4. Click **Deploy** — no additional configuration needed.

The app auto-installs from `requirements.txt`. `football_players.csv` is committed to the
repo, so no generation step is required at deploy time.

---

## 🛠️ Running the Data Generator Standalone

```bash
python generate_data.py
```

This regenerates `football_players.csv` with the same seed, producing byte-identical output.

---

## 📄 Licence

This project is released under the [MIT Licence](https://opensource.org/licenses/MIT).
Use it freely for learning, portfolios, and personal projects.
