"""
app.py
------
Football Player Performance Analytics Dashboard
Powered by Streamlit + Plotly

⚠️  All data is SYNTHETIC and does NOT represent real-world football statistics.

Run:
    streamlit run app.py
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. Page configuration  (must be the FIRST Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. CSS — dark football-inspired theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Global background ── */
    .stApp { background-color: #0e1117; color: #e6edf3; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }

    /* ── KPI cards ── */
    .kpi-card {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-left: 4px solid #00ff87;
        border-radius: 8px;
        padding: 18px 20px;
        text-align: center;
    }
    .kpi-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #00ff87;
    }
    .kpi-sub {
        font-size: 12px;
        color: #8b949e;
        margin-top: 4px;
    }

    /* ── Section headings ── */
    h2, h3 { color: #e6edf3; }

    /* ── Plotly chart container ── */
    .js-plotly-plot { border-radius: 8px; }

    /* ── Streamlit metric delta colour override ── */
    [data-testid="stMetricDelta"] { color: #00ff87 !important; }

    /* ── Download button ── */
    .stDownloadButton > button {
        background-color: #238636;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    .stDownloadButton > button:hover { background-color: #2ea043; }

    /* ── Disclaimer banner ── */
    .synthetic-banner {
        background-color: #1f2937;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 10px 16px;
        color: #fbbf24;
        font-size: 13px;
        margin-bottom: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 3. Data loading & caching
# ---------------------------------------------------------------------------
CSV_PATH = "football_players.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load dataset from CSV; generate it first if absent."""
    if not os.path.exists(path):
        st.toast("CSV not found — generating synthetic dataset…", icon="⚙️")
        from generate_data import generate_dataset
        generate_dataset(path)
    df = pd.read_csv(path)
    return df


df_raw = load_data(CSV_PATH)

# ---------------------------------------------------------------------------
# 4. Sidebar — navigation + filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚽ Football Analytics")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["Overview", "Player Analysis", "Team Analysis", "Position Analysis"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    # Season
    seasons = ["All"] + sorted(df_raw["season"].unique().tolist())
    sel_season = st.selectbox("Season", seasons)

    # Team — depends on season filter
    df_s = df_raw if sel_season == "All" else df_raw[df_raw["season"] == sel_season]
    teams = ["All"] + sorted(df_s["team"].unique().tolist())
    sel_team = st.selectbox("Team", teams)

    # Position
    positions = ["All"] + sorted(df_raw["position"].unique().tolist())
    sel_position = st.selectbox("Position", positions)

    # Player multi-select — narrows to season+team+position slice
    df_stacked = df_s.copy()
    if sel_team != "All":
        df_stacked = df_stacked[df_stacked["team"] == sel_team]
    if sel_position != "All":
        df_stacked = df_stacked[df_stacked["position"] == sel_position]

    player_options = sorted(df_stacked["player_name"].unique().tolist())
    sel_players = st.multiselect("Player(s)", player_options, default=[])

    # Reset filters button
    if st.button("↺  Reset Filters"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.caption("⚠️ All data is **synthetic** and does not represent real football statistics.")

# ---------------------------------------------------------------------------
# 5. Apply filters
# ---------------------------------------------------------------------------
df = df_raw.copy()

if sel_season != "All":
    df = df[df["season"] == sel_season]
if sel_team != "All":
    df = df[df["team"] == sel_team]
if sel_position != "All":
    df = df[df["position"] == sel_position]
if sel_players:
    df = df[df["player_name"].isin(sel_players)]

# ---------------------------------------------------------------------------
# 6. Validation guard
# ---------------------------------------------------------------------------
def _empty_state_guard(df: pd.DataFrame) -> bool:
    """Show a warning and return False if the filtered DataFrame is empty."""
    if len(df) == 0:
        st.warning(
            "⚠️ No players match the current filters. "
            "Try broadening your selection or click **↺ Reset Filters** in the sidebar.",
            icon="🔍",
        )
        return False
    return True

# ---------------------------------------------------------------------------
# 7. Shared utilities
# ---------------------------------------------------------------------------
DARK_TEMPLATE = "plotly_dark"
GREEN = "#00ff87"
ACCENT_COLORS = [
    "#00ff87", "#00b4d8", "#f59e0b", "#f43f5e",
    "#a78bfa", "#34d399", "#fb923c", "#60a5fa",
]

POSITION_COLORS = {
    "GK": "#f59e0b",
    "DEF": "#00b4d8",
    "MID": "#a78bfa",
    "FWD": "#f43f5e",
}


def _chart_layout(fig, height: int = 420):
    """Apply consistent layout settings to every chart."""
    fig.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(color="#e6edf3", size=12),
        margin=dict(l=40, r=20, t=50, b=40),
        height=height,
        legend=dict(bgcolor="#0e1117", bordercolor="#21262d", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="#21262d", zerolinecolor="#21262d")
    fig.update_yaxes(gridcolor="#21262d", zerolinecolor="#21262d")
    return fig


def render_data_table(df: pd.DataFrame, key_prefix: str = ""):
    """Searchable player statistics table with CSV download."""
    st.markdown("### 📋 Player Statistics Table")

    search = st.text_input(
        "Search player by name",
        placeholder="e.g. Luca Silva",
        key=f"{key_prefix}_search",
    )
    display_df = df.copy()
    if search.strip():
        mask = display_df["player_name"].str.contains(search.strip(), case=False, na=False)
        display_df = display_df[mask]

    st.dataframe(
        display_df.reset_index(drop=True),
        width="stretch",
        height=320,
    )

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download filtered data as CSV",
        data=csv_bytes,
        file_name="football_players_filtered.csv",
        mime="text/csv",
        key=f"{key_prefix}_download",
    )


def _synthetic_banner():
    st.markdown(
        '<div class="synthetic-banner">'
        "⚠️ <strong>Synthetic Data Notice:</strong> All player names, teams, and statistics "
        "are randomly generated for demonstration purposes only. "
        "They do <strong>not</strong> represent real football results."
        "</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 8. Page functions
# ---------------------------------------------------------------------------

# ── 8a. Overview ────────────────────────────────────────────────────────────

def page_overview(df: pd.DataFrame):
    st.markdown("# 📊 Dashboard Overview")
    _synthetic_banner()

    if not _empty_state_guard(df):
        return

    # KPI calculations
    total_players  = df["player_id"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(float(df["rating"].mean()), 2)

    # KPI cards via custom HTML for consistent styling
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, value, sub in [
        (c1, "Total Players",   f"{total_players:,}",   "unique players"),
        (c2, "Total Goals",     f"{total_goals:,}",     "across selection"),
        (c3, "Total Assists",   f"{total_assists:,}",   "across selection"),
        (c4, "Minutes Played",  f"{total_minutes:,}",   "total minutes"),
        (c5, "Avg Rating",      f"{avg_rating}",        "out of 9.5"),
    ]:
        col.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Top-10 leaderboard
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 🏆 Top 10 Players")
        top10 = (
            df[["player_name", "team", "position", "season", "goals", "assists",
                "minutes_played", "rating"]]
            .sort_values(["goals", "assists"], ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        top10.index += 1  # 1-based rank
        st.dataframe(top10, width="stretch", height=360)

    with col_right:
        # Goals distribution by position pie
        pos_goals = df.groupby("position")["goals"].sum().reset_index()
        fig_pie = px.pie(
            pos_goals,
            names="position",
            values="goals",
            title="Goals by Position",
            color="position",
            color_discrete_map=POSITION_COLORS,
            template=DARK_TEMPLATE,
            hole=0.4,
        )
        _chart_layout(fig_pie, height=360)
        st.plotly_chart(fig_pie, width="stretch")

    st.markdown("---")
    render_data_table(df, key_prefix="overview")


# ── 8b. Player Analysis ─────────────────────────────────────────────────────

def page_player(df: pd.DataFrame):
    st.markdown("# 👤 Player Analysis")
    _synthetic_banner()

    if not _empty_state_guard(df):
        return

    # Derived column: shot conversion rate
    df = df.copy()
    df["conversion_rate"] = (
        df["goals"] / df["shots"].replace(0, np.nan)
    ).fillna(0).round(3)

    # ── Scatter 1: Goals vs Assists ──────────────────────────────────────────
    st.markdown("### ⚡ Goals vs Assists")
    fig_ga = px.scatter(
        df,
        x="assists",
        y="goals",
        color="position",
        color_discrete_map=POSITION_COLORS,
        hover_data=["player_name", "team", "season", "appearances"],
        size="appearances",
        size_max=18,
        title="Goals vs Assists (size = appearances)",
        labels={"assists": "Assists", "goals": "Goals"},
        template=DARK_TEMPLATE,
    )
    _chart_layout(fig_ga)
    st.plotly_chart(fig_ga, width="stretch")

    # ── Scatter 2: Shots vs Goals ────────────────────────────────────────────
    st.markdown("### 🎯 Shots vs Goals (Conversion Efficiency)")
    fig_sg = px.scatter(
        df,
        x="shots",
        y="goals",
        color="position",
        color_discrete_map=POSITION_COLORS,
        hover_data=["player_name", "team", "conversion_rate"],
        size="appearances",
        size_max=18,
        title="Shots vs Goals (hover for conversion rate)",
        labels={"shots": "Total Shots", "goals": "Goals Scored"},
        template=DARK_TEMPLATE,
    )
    _chart_layout(fig_sg)
    st.plotly_chart(fig_sg, width="stretch")

    # ── Radar: Player Comparison ─────────────────────────────────────────────
    st.markdown("### 📡 Player Comparison Radar")
    st.caption("Select up to 3 players to compare across 6 key stats.")

    all_players = sorted(df["player_name"].unique().tolist())
    selected = st.multiselect(
        "Choose players to compare",
        all_players,
        default=all_players[:2] if len(all_players) >= 2 else all_players,
        key="radar_select",
    )

    if len(selected) > 3:
        st.warning("Please select at most 3 players for a clean comparison.", icon="⚠️")
        selected = selected[:3]

    if selected:
        radar_cols = ["goals", "assists", "rating", "tackles", "passes", "shots"]
        radar_labels = ["Goals", "Assists", "Rating", "Tackles", "Passes", "Shots"]

        sub = df[df["player_name"].isin(selected)].groupby("player_name")[radar_cols].mean()

        # Normalise each stat to 0–1 range across the full filtered dataset
        stat_max = df[radar_cols].max()
        stat_max = stat_max.replace(0, 1)  # avoid division by zero

        fig_radar = go.Figure()
        for i, player in enumerate(selected):
            if player not in sub.index:
                continue
            vals = (sub.loc[player] / stat_max).values.tolist()
            vals += [vals[0]]  # close the polygon
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals,
                    theta=radar_labels + [radar_labels[0]],
                    fill="toself",
                    name=player,
                    line=dict(color=ACCENT_COLORS[i % len(ACCENT_COLORS)]),
                    fillcolor=ACCENT_COLORS[i % len(ACCENT_COLORS)],
                    opacity=0.25,
                )
            )

        fig_radar.update_layout(
            polar=dict(
                bgcolor="#161b22",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor="#21262d",
                    tickfont=dict(color="#8b949e", size=9),
                ),
                angularaxis=dict(gridcolor="#21262d"),
            ),
            paper_bgcolor="#161b22",
            font=dict(color="#e6edf3"),
            legend=dict(bgcolor="#0e1117"),
            title="Normalised Player Comparison (0–1 scale)",
            template=DARK_TEMPLATE,
            height=480,
        )
        st.plotly_chart(fig_radar, width="stretch")
    else:
        st.info("Select at least one player above to display the radar chart.")

    st.markdown("---")
    render_data_table(df, key_prefix="player")


# ── 8c. Team Analysis ───────────────────────────────────────────────────────

def page_team(df: pd.DataFrame):
    st.markdown("# 🏟️ Team Analysis")
    _synthetic_banner()

    if not _empty_state_guard(df):
        return

    # Aggregate by team
    team_agg = (
        df.groupby("team")
        .agg(
            total_goals=("goals", "sum"),
            total_assists=("assists", "sum"),
            total_shots=("shots", "sum"),
            avg_rating=("rating", "mean"),
            player_count=("player_id", "nunique"),
        )
        .reset_index()
    )
    team_agg["avg_rating"] = team_agg["avg_rating"].round(2)
    team_agg = team_agg.sort_values("total_goals", ascending=False)

    # ── Grouped bar: Goals & Assists per team ────────────────────────────────
    st.markdown("### ⚽ Goals & Assists per Team")
    fig_ga = px.bar(
        team_agg.melt(id_vars="team", value_vars=["total_goals", "total_assists"],
                      var_name="metric", value_name="count"),
        x="team",
        y="count",
        color="metric",
        barmode="group",
        color_discrete_map={"total_goals": GREEN, "total_assists": "#00b4d8"},
        labels={"team": "Club", "count": "Total", "metric": "Metric"},
        title="Total Goals and Assists by Team",
        template=DARK_TEMPLATE,
    )
    _chart_layout(fig_ga, height=400)
    fig_ga.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_ga, width="stretch")

    col_left, col_right = st.columns(2)

    # ── Bar: Player count ────────────────────────────────────────────────────
    with col_left:
        st.markdown("### 👥 Squad Size per Team")
        fig_pc = px.bar(
            team_agg,
            x="team",
            y="player_count",
            color="player_count",
            color_continuous_scale=[[0, "#21262d"], [1, GREEN]],
            labels={"team": "Club", "player_count": "Players"},
            title="Number of Players per Team",
            template=DARK_TEMPLATE,
        )
        _chart_layout(fig_pc, height=360)
        fig_pc.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_pc, width="stretch")

    # ── Bar: Average rating ──────────────────────────────────────────────────
    with col_right:
        st.markdown("### ⭐ Average Rating per Team")
        fig_ar = px.bar(
            team_agg,
            x="team",
            y="avg_rating",
            color="avg_rating",
            color_continuous_scale=[[0, "#21262d"], [1, "#f59e0b"]],
            labels={"team": "Club", "avg_rating": "Avg Rating"},
            title="Average Player Rating by Team",
            template=DARK_TEMPLATE,
        )
        fig_ar.update_layout(yaxis=dict(range=[0, 10]))
        _chart_layout(fig_ar, height=360)
        fig_ar.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_ar, width="stretch")

    # ── Team summary table ───────────────────────────────────────────────────
    st.markdown("### 📋 Team Summary Table")
    display_agg = team_agg.rename(columns={
        "team": "Club",
        "total_goals": "Goals",
        "total_assists": "Assists",
        "total_shots": "Shots",
        "avg_rating": "Avg Rating",
        "player_count": "Players",
    })
    st.dataframe(display_agg.reset_index(drop=True), width="stretch")

    st.markdown("---")
    render_data_table(df, key_prefix="team")


# ── 8d. Position Analysis ────────────────────────────────────────────────────

def page_position(df: pd.DataFrame):
    st.markdown("# 🎽 Position Analysis")
    _synthetic_banner()

    if not _empty_state_guard(df):
        return

    # ── Position-specific callout metrics ────────────────────────────────────
    st.markdown("### 📌 Position Highlights")
    pos_data = df.groupby("position")

    c_gk, c_def, c_mid, c_fwd = st.columns(4)

    def _safe_mean(df_pos, col):
        sub = df[df["position"] == df_pos]
        return round(float(sub[col].mean()), 1) if len(sub) > 0 else "N/A"

    c_gk.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">🧤 GK — Avg Saves</div>'
        f'<div class="kpi-value">{_safe_mean("GK", "saves")}</div>'
        f'<div class="kpi-sub">per goalkeeper</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    c_def.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">🛡️ DEF — Avg Tackles</div>'
        f'<div class="kpi-value">{_safe_mean("DEF", "tackles")}</div>'
        f'<div class="kpi-sub">per defender</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    c_mid.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">🎯 MID — Avg Key Passes</div>'
        f'<div class="kpi-value">{_safe_mean("MID", "key_passes")}</div>'
        f'<div class="kpi-sub">per midfielder</div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    c_fwd.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">⚡ FWD — Avg Goals</div>'
        f'<div class="kpi-value">{_safe_mean("FWD", "goals")}</div>'
        f'<div class="kpi-sub">per forward</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Box plot: Rating by position ──────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### 📦 Rating Distribution by Position")
        fig_box = px.box(
            df,
            x="position",
            y="rating",
            color="position",
            color_discrete_map=POSITION_COLORS,
            points="outliers",
            title="Player Rating Distribution (box plot)",
            labels={"position": "Position", "rating": "Rating"},
            template=DARK_TEMPLATE,
            category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
        )
        _chart_layout(fig_box, height=400)
        st.plotly_chart(fig_box, width="stretch")

    # ── Stacked bar: Goals & Assists by position ──────────────────────────────
    with col_r:
        st.markdown("### 📊 Goals & Assists by Position")
        pos_stats = (
            df.groupby("position")[["goals", "assists"]]
            .sum()
            .reset_index()
            .melt(id_vars="position", value_vars=["goals", "assists"],
                  var_name="metric", value_name="total")
        )
        fig_stacked = px.bar(
            pos_stats,
            x="position",
            y="total",
            color="metric",
            barmode="stack",
            color_discrete_map={"goals": GREEN, "assists": "#00b4d8"},
            labels={"position": "Position", "total": "Total", "metric": "Metric"},
            title="Total Goals and Assists by Position",
            template=DARK_TEMPLATE,
            category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
        )
        _chart_layout(fig_stacked, height=400)
        st.plotly_chart(fig_stacked, width="stretch")

    # ── Violin: Minutes played by position ───────────────────────────────────
    st.markdown("### ⏱️ Minutes Played Distribution by Position")
    fig_violin = px.violin(
        df,
        x="position",
        y="minutes_played",
        color="position",
        color_discrete_map=POSITION_COLORS,
        box=True,
        points="outliers",
        title="Minutes Played per Player by Position",
        labels={"position": "Position", "minutes_played": "Minutes Played"},
        template=DARK_TEMPLATE,
        category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
    )
    _chart_layout(fig_violin, height=380)
    st.plotly_chart(fig_violin, width="stretch")

    st.markdown("---")
    render_data_table(df, key_prefix="position")


# ---------------------------------------------------------------------------
# 9. Page router
# ---------------------------------------------------------------------------
if page == "Overview":
    page_overview(df)
elif page == "Player Analysis":
    page_player(df)
elif page == "Team Analysis":
    page_team(df)
elif page == "Position Analysis":
    page_position(df)
