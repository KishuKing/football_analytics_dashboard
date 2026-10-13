"""
generate_data.py
----------------
Generates a reproducible synthetic football (soccer) player dataset.
All statistics are SYNTHETIC and do NOT represent real-world football results.

Run directly:
    python generate_data.py

Or import and call generate_dataset() from app.py if the CSV is missing.
"""

import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
OUTPUT_FILE = "football_players.csv"
N_PLAYERS = 120  # per season → 240 total rows

TEAMS = [
    "FC Northgate",
    "Southfield United",
    "Eastbrook City",
    "Westmoor Athletic",
    "Riverside FC",
    "Lakeside Wanderers",
    "Hillcrest Rangers",
    "Portview Town",
]

SEASONS = ["2022-23", "2023-24"]

# Position distribution weights: GK 8%, DEF 28%, MID 36%, FWD 28%
POSITIONS = ["GK", "DEF", "MID", "FWD"]
POSITION_WEIGHTS = [0.08, 0.28, 0.36, 0.28]

FIRST_NAMES = [
    "Luca", "Marcus", "Tomás", "Diego", "Alexei", "Samuel", "Jordan", "Finn",
    "Omar", "Rafael", "Kai", "Henrik", "Carlos", "James", "Yusuf", "Patrick",
    "Eduardo", "Nils", "Arjun", "Mohammed", "Leon", "Felix", "Stefan", "Bruno",
    "Cristian", "Mateo", "Ivan", "Aaron", "Theo", "Elias",
]
LAST_NAMES = [
    "Silva", "Müller", "García", "Johnson", "Petrov", "Rossi", "Nakamura",
    "Okonkwo", "Dubois", "Santos", "Weber", "Andersen", "Kovač", "Olsson",
    "Fernández", "Martínez", "Nguyen", "Klein", "Patel", "Hoffmann",
    "Larsson", "Barroso", "Diallo", "Eriksen", "Herrera", "Castillo",
    "Becker", "Moreau", "Tanaka", "Adeyemi",
]


# ---------------------------------------------------------------------------
# Per-position stat generators
# ---------------------------------------------------------------------------

def _stats_for_position(position: str, appearances: int, rng: np.random.Generator) -> dict:
    """Return a dict of stats appropriate for the given position."""
    a = appearances  # shorthand

    if position == "GK":
        goals        = int(rng.integers(0, 2))
        assists      = int(rng.integers(0, 2))
        shots        = int(rng.integers(0, 5))
        tackles      = int(rng.integers(0, a // 3 + 1))
        interceptions = int(rng.integers(0, a // 4 + 1))
        passes       = int(rng.integers(a * 15, a * 35))
        key_passes   = int(rng.integers(0, max(1, passes // 20)))
        clean_sheets = int(rng.integers(0, max(1, a // 2)))
        saves        = int(rng.integers(a * 2, a * 5))

    elif position == "DEF":
        goals        = int(rng.integers(0, max(1, a // 6)))
        assists      = int(rng.integers(0, max(1, a // 5)))
        shots        = int(rng.integers(0, max(1, a // 4)))
        tackles      = int(rng.integers(a // 2, a * 3))
        interceptions = int(rng.integers(a // 3, a * 2))
        passes       = int(rng.integers(a * 20, a * 60))
        key_passes   = int(rng.integers(0, max(1, passes // 15)))
        clean_sheets = int(rng.integers(0, max(1, a // 4)))
        saves        = int(rng.integers(0, 3))

    elif position == "MID":
        goals        = int(rng.integers(0, max(1, a // 4)))
        assists      = int(rng.integers(0, max(1, a // 3)))
        shots        = int(rng.integers(0, max(1, a // 2)))
        tackles      = int(rng.integers(a // 4, a * 2))
        interceptions = int(rng.integers(a // 5, a))
        passes       = int(rng.integers(a * 30, a * 80))
        key_passes   = int(rng.integers(0, max(1, passes // 10)))
        clean_sheets = 0
        saves        = 0

    else:  # FWD
        goals        = int(rng.integers(0, max(1, a // 2)))
        assists      = int(rng.integers(0, max(1, a // 3)))
        shots        = int(rng.integers(max(1, a // 2), a * 3))
        tackles      = int(rng.integers(0, max(1, a // 5)))
        interceptions = int(rng.integers(0, max(1, a // 6)))
        passes       = int(rng.integers(a * 10, a * 40))
        key_passes   = int(rng.integers(0, max(1, passes // 12)))
        clean_sheets = 0
        saves        = 0

    shots_on_target = int(rng.integers(0, max(1, shots + 1)))
    shots_on_target = min(shots_on_target, shots)  # enforce constraint
    key_passes      = min(key_passes, passes // 5 + 1)  # enforce constraint

    yellow_cards = int(rng.integers(0, 11))
    red_cards    = int(rng.integers(0, 3))
    minutes_played = int(a * rng.integers(60, 91))
    rating       = round(float(rng.uniform(5.0, 9.5)), 1)

    return dict(
        goals=goals, assists=assists, shots=shots,
        shots_on_target=shots_on_target, passes=passes, key_passes=key_passes,
        tackles=tackles, interceptions=interceptions,
        yellow_cards=yellow_cards, red_cards=red_cards,
        minutes_played=minutes_played, rating=rating,
        clean_sheets=clean_sheets, saves=saves,
    )


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_dataset(output_file: str = OUTPUT_FILE) -> pd.DataFrame:
    """Generate and save the synthetic dataset. Returns the DataFrame."""
    rng = np.random.default_rng(SEED)
    records = []
    player_id = 1

    for season in SEASONS:
        # Assign each of the N_PLAYERS a team and position
        teams     = rng.choice(TEAMS, size=N_PLAYERS)
        positions = rng.choice(POSITIONS, size=N_PLAYERS, p=POSITION_WEIGHTS)
        ages      = rng.integers(18, 37, size=N_PLAYERS)
        appearances = rng.integers(1, 39, size=N_PLAYERS)

        # Build name pool — combine first+last, shuffle reproducibly
        name_pool = [
            f"{f} {l}" for f in FIRST_NAMES for l in LAST_NAMES
        ]
        rng.shuffle(name_pool)

        for i in range(N_PLAYERS):
            name = name_pool[i % len(name_pool)]
            stats = _stats_for_position(positions[i], int(appearances[i]), rng)
            records.append({
                "player_id":    player_id,
                "player_name":  name,
                "team":         teams[i],
                "position":     positions[i],
                "season":       season,
                "age":          int(ages[i]),
                "appearances":  int(appearances[i]),
                **stats,
            })
            player_id += 1

    df = pd.DataFrame(records)

    # Reorder columns to match schema
    col_order = [
        "player_id", "player_name", "team", "position", "season", "age",
        "appearances", "goals", "assists", "shots", "shots_on_target",
        "passes", "key_passes", "tackles", "interceptions",
        "yellow_cards", "red_cards", "minutes_played", "rating",
        "clean_sheets", "saves",
    ]
    df = df[col_order]

    df.to_csv(output_file, index=False)
    print(f"[generate_data] Saved {len(df)} rows to '{output_file}'")
    return df


if __name__ == "__main__":
    df = generate_dataset()
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Nulls:\n{df.isnull().sum()}")
    print(f"\nPositions:\n{df['position'].value_counts()}")
    print(f"\nSeasons:\n{df['season'].value_counts()}")
