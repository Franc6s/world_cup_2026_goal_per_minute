from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent

GOALS_FILE = BASE_DIR / "goals.xlsx"
MANAGERS_FILE = BASE_DIR / "managers.xlsx"


# ============================================================
# THEME
# ============================================================
NAVY = "#061A2D"
DARK_BLUE = "#0A2E52"
BLUE = "#125CA8"
MID_BLUE = "#2F78BE"
LIGHT_BLUE = "#D9EAF7"
PALE_BLUE = "#EEF6FC"

GOLD = "#D4AF37"
LIGHT_GOLD = "#F2DE91"

WHITE = "#FFFFFF"
OFF_WHITE = "#F7F9FC"
TEXT = "#102A43"
MUTED = "#6B7C93"
BORDER = "#D8E2EC"

CONFED_COLORS = {
    "AFC": "#0B4F8A",
    "CAF": "#1769AA",
    "CONCACAF": "#3C87C8",
    "CONMEBOL": "#D4AF37",
    "OFC": "#AFCDEA",
    "UEFA": "#6D92B8",
}


# ============================================================
# LOAD + CLEAN DATA
# ============================================================
def clean_column_name(col):
    return (
        str(col)
        .replace("\n", " ")
        .strip()
        .replace("  ", " ")
    )


goals = pd.read_excel(GOALS_FILE, sheet_name="All Goals")
goals.columns = [clean_column_name(c) for c in goals.columns]

managers = pd.read_excel(MANAGERS_FILE, sheet_name="Manager")
managers.columns = [clean_column_name(c) for c in managers.columns]

# Normalize a few column names that have spaces/newlines in Excel.
rename_goals = {
    "Minute Scored": "Minute Scored",
    "Stoppage Time goal (min)": "Stoppage Goal Min",
    "Penalty Shout out Winner": "Penalty Shootout Winner",
}
goals = goals.rename(columns=rename_goals)

rename_managers = {
    "Coach": "Coach",
}
managers = managers.rename(columns=rename_managers)

# Strip whitespace from text columns.
for col in goals.select_dtypes(include="object").columns:
    goals[col] = goals[col].astype(str).str.strip()
    goals[col] = goals[col].replace({"nan": np.nan, "None": np.nan})

for col in managers.select_dtypes(include="object").columns:
    managers[col] = managers[col].astype(str).str.strip()
    managers[col] = managers[col].replace({"nan": np.nan, "None": np.nan})

# Numeric cleanup.
goals["Minute Scored"] = pd.to_numeric(goals["Minute Scored"], errors="coerce")
goals["Player Age"] = pd.to_numeric(goals["Player Age"], errors="coerce")
goals["Attendance"] = pd.to_numeric(goals["Attendance"], errors="coerce")
goals["Stoppage Goal Min"] = pd.to_numeric(
    goals.get("Stoppage Goal Min", 0), errors="coerce"
).fillna(0)

# One goal event = one valid Goal_ID.
goals = goals[goals["Goal_ID"].notna()].copy()

# Keep shootout rows separately if your dataset eventually contains them.
goals["Is Shootout"] = (
    goals["Penalty Shoot-Out"]
    .fillna("No")
    .astype(str)
    .str.lower()
    .isin(["yes", "y", "true", "1"])
)

# Regulation/extra-time scoring dataset, excluding shootout conversions.
goal_events = goals[~goals["Is Shootout"]].copy()

# Derived bins for scoring analysis.
bins = [0, 15, 30, 45, 60, 75, 90, 105, 120, np.inf]
labels = [
    "1–15",
    "16–30",
    "31–45",
    "46–60",
    "61–75",
    "76–90",
    "91–105",
    "106–120",
    "120+",
]
goal_events["Goal Period"] = pd.cut(
    goal_events["Minute Scored"],
    bins=bins,
    labels=labels,
    include_lowest=True,
    right=True,
)

age_bins = [0, 20, 24, 28, 32, np.inf]
age_labels = ["≤20", "21–24", "25–28", "29–32", "33+"]
goal_events["Age Band"] = pd.cut(
    goal_events["Player Age"],
    bins=age_bins,
    labels=age_labels,
    include_lowest=True,
)

# Broad position families.
POSITION_MAP = {
    "GK": "Goalkeeper",
    "CB": "Defender",
    "DF": "Defender",
    "LB": "Defender",
    "RB": "Defender",
    "LWB": "Defender",
    "RWB": "Defender",
    "DM": "Midfielder",
    "CM": "Midfielder",
    "MF": "Midfielder",
    "LM": "Midfielder",
    "RM": "Midfielder",
    "AM": "Midfielder",
    "LW": "Forward",
    "RW": "Forward",
    "LF": "Forward",
    "RF": "Forward",
    "CF": "Forward",
    "ST": "Forward",
    "FW": "Forward",
}
goal_events["Position Group"] = (
    goal_events["Player Position"]
    .map(POSITION_MAP)
    .fillna("Other")
)

# Merge manager data for country profile.
country_info = managers.rename(
    columns={
        "National Team": "Player Country",
        "Nationality": "Coach Nationality",
    }
)[["Player Country", "Coach", "Coach Nationality"]].drop_duplicates()

goal_events = goal_events.merge(country_info, on="Player Country", how="left")

# Match-level view for metrics that can safely be calculated from matches
# represented in the goal file.
match_level = (
    goal_events.sort_values(["Match ID", "Goal_ID"])
    .drop_duplicates("Match ID")
    .copy()
)

# Attendance must only be counted once per match.
venue_matches = (
    goal_events[
        ["Match ID", "Country Venue", "City Venue", "Stadium Name", "Attendance"]
    ]
    .drop_duplicates("Match ID")
    .copy()
)

