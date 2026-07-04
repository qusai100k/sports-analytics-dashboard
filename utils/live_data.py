from __future__ import annotations

import json
import os
import re
import ssl
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "dataset" / "cache"

PREMIER_LEAGUE_CLUBS = [
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton",
    "Burnley",
    "Chelsea",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Leeds United",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Newcastle United",
    "Nottingham Forest",
    "Sunderland",
    "Tottenham Hotspur",
    "West Ham United",
    "Wolverhampton Wanderers",
]

FOOTBALL_DATA_CSVS = {
    2020: "http://www.football-data.co.uk/mmz4281/2021/E0.csv",
    2021: "http://www.football-data.co.uk/mmz4281/2122/E0.csv",
    2022: "http://www.football-data.co.uk/mmz4281/2223/E0.csv",
    2023: "http://www.football-data.co.uk/mmz4281/2324/E0.csv",
    2024: "http://www.football-data.co.uk/mmz4281/2425/E0.csv",
    2025: "http://www.football-data.co.uk/mmz4281/2526/E0.csv",
}

OPENFOOTBALL_EPL_FILES = {
    2021: "https://raw.githubusercontent.com/openfootball/england/master/2021-22/1-premierleague.txt",
    2022: "https://raw.githubusercontent.com/openfootball/england/master/2022-23/1-premierleague.txt",
    2023: "https://raw.githubusercontent.com/openfootball/england/master/2023-24/1-premierleague.txt",
    2024: "https://raw.githubusercontent.com/openfootball/england/master/2024-25/1-premierleague.txt",
    2025: "https://raw.githubusercontent.com/openfootball/england/master/2025-26/1-premierleague.txt",
}


def _request_json(url: str, headers: Optional[dict[str, str]] = None) -> dict:
    request = Request(url, headers=headers or {"User-Agent": "sports-analytics-capstone/1.0"})
    with urlopen(request, timeout=18) as response:
        return json.loads(response.read().decode("utf-8"))


def _read_provider_csv(url: str) -> pd.DataFrame:
    request = Request(url, headers={"User-Agent": "sports-analytics-capstone/1.0"})
    try:
        with urlopen(request, timeout=12) as response:
            return pd.read_csv(BytesIO(response.read()))
    except Exception:
        secure_url = url.replace("http://", "https://")
        context = ssl._create_unverified_context()
        with urlopen(Request(secure_url, headers={"User-Agent": "sports-analytics-capstone/1.0"}), timeout=12, context=context) as response:
            return pd.read_csv(BytesIO(response.read()))


def _read_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "sports-analytics-capstone/1.0"})
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


def _clean_club_name(name: str) -> str:
    replacements = {
        "Manchester United FC": "Manchester United",
        "Manchester City FC": "Manchester City",
        "Tottenham Hotspur FC": "Tottenham Hotspur",
        "Newcastle United FC": "Newcastle United",
        "Nottingham Forest FC": "Nottingham Forest",
        "West Ham United FC": "West Ham United",
        "Wolverhampton Wanderers FC": "Wolverhampton Wanderers",
        "Brighton & Hove Albion FC": "Brighton",
        "AFC Bournemouth": "Bournemouth",
        "Leicester City FC": "Leicester City",
        "Southampton FC": "Southampton",
        "Ipswich Town FC": "Ipswich Town",
        "Leeds United FC": "Leeds United",
        "Sunderland AFC": "Sunderland",
    }
    return replacements.get(name.strip(), name.strip().replace(" FC", ""))


def _parse_openfootball_text(text: str, season: int) -> pd.DataFrame:
    rows = []
    date_hint = pd.Timestamp(f"{season}-08-01")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("=", "#", "▪")):
            continue
        date_match = re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})(?:\s+(\d{4}))?", line)
        if date_match:
            month = date_match.group(2)
            day = int(date_match.group(3))
            year = int(date_match.group(4) or (season if month in {"Aug", "Sep", "Oct", "Nov", "Dec"} else season + 1))
            date_hint = pd.to_datetime(f"{year} {month} {day}", errors="coerce")
            continue
        match = re.match(
            r"^(?:\d{1,2}:\d{2}\s+)?(.+?)\s{2,}v\s(.+?)\s{2,}(\d+)-(\d+)(?:\s+\(.*\))?$",
            line,
        )
        if not match:
            continue
        home_team, away_team, home_goals, away_goals = match.groups()
        home_goals_i = int(home_goals)
        away_goals_i = int(away_goals)
        result = "Home Win" if home_goals_i > away_goals_i else "Away Win" if away_goals_i > home_goals_i else "Draw"
        rows.append(
            {
                "date": date_hint,
                "season": season,
                "league": "Premier League",
                "home_team": _clean_club_name(home_team),
                "away_team": _clean_club_name(away_team),
                "home_goals": home_goals_i,
                "away_goals": away_goals_i,
                "home_shots": 0,
                "away_shots": 0,
                "result": result,
            }
        )
    return pd.DataFrame(rows)


def load_openfootball_premier_league_matches(force_refresh: bool = False) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / "openfootball_epl.csv"
    if cache_path.exists() and not force_refresh:
        return pd.read_csv(cache_path, parse_dates=["date"])

    frames = []
    for season, url in OPENFOOTBALL_EPL_FILES.items():
        try:
            parsed = _parse_openfootball_text(_read_text(url), season)
            if not parsed.empty:
                frames.append(parsed)
        except Exception:
            continue
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(["date", "home_team", "away_team"])
        combined.to_csv(cache_path, index=False)
        return combined
    if cache_path.exists():
        return pd.read_csv(cache_path, parse_dates=["date"])
    return pd.DataFrame()


def _normalize_football_data_csv(df: pd.DataFrame, season: int) -> pd.DataFrame:
    required = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
    if not set(required).issubset(df.columns):
        return pd.DataFrame()
    out = df[required + [col for col in ["HS", "AS", "HST", "AST"] if col in df.columns]].copy()
    out = out.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"])
    out["date"] = pd.to_datetime(out["Date"], dayfirst=True, errors="coerce")
    out = out.dropna(subset=["date"])
    out["season"] = season
    out["league"] = "Premier League"
    out["home_team"] = out["HomeTeam"].replace({"Man City": "Manchester City", "Man United": "Manchester United"})
    out["away_team"] = out["AwayTeam"].replace({"Man City": "Manchester City", "Man United": "Manchester United"})
    out["home_goals"] = out["FTHG"].astype(int)
    out["away_goals"] = out["FTAG"].astype(int)
    out["result"] = out["FTR"].map({"H": "Home Win", "D": "Draw", "A": "Away Win"})
    out["home_shots"] = pd.to_numeric(out.get("HS", 0), errors="coerce").fillna(0).astype(int)
    out["away_shots"] = pd.to_numeric(out.get("AS", 0), errors="coerce").fillna(0).astype(int)
    return out[["date", "season", "league", "home_team", "away_team", "home_goals", "away_goals", "home_shots", "away_shots", "result"]]


def load_public_premier_league_matches(force_refresh: bool = False) -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    openfootball = load_openfootball_premier_league_matches(force_refresh=force_refresh)
    if not openfootball.empty:
        return openfootball

    cache_path = CACHE_DIR / "football_data_uk_epl.csv"
    if cache_path.exists() and not force_refresh:
        return pd.read_csv(cache_path, parse_dates=["date"])

    frames = []
    for season, url in FOOTBALL_DATA_CSVS.items():
        try:
            raw = _read_provider_csv(url)
            normalized = _normalize_football_data_csv(raw, season)
            if not normalized.empty:
                frames.append(normalized)
        except (URLError, TimeoutError, ValueError, OSError):
            continue

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(["date", "home_team", "away_team"])
        combined.to_csv(cache_path, index=False)
        return combined
    if cache_path.exists():
        return pd.read_csv(cache_path, parse_dates=["date"])
    return pd.DataFrame()


def fetch_football_data_org_teams() -> dict:
    api_key = os.getenv("FOOTBALL_DATA_API_KEY", "").strip()
    if not api_key:
        return {"provider": "football-data.org", "configured": False, "teams": []}
    data = _request_json(
        "https://api.football-data.org/v4/competitions/PL/teams",
        headers={"X-Auth-Token": api_key, "User-Agent": "sports-analytics-capstone/1.0"},
    )
    teams = [team.get("name") for team in data.get("teams", []) if team.get("name")]
    return {"provider": "football-data.org", "configured": True, "teams": teams}


def fetch_api_football_teams() -> dict:
    api_key = os.getenv("API_FOOTBALL_KEY", "").strip()
    if not api_key:
        return {"provider": "API-Football", "configured": False, "teams": []}
    data = _request_json(
        "https://v3.football.api-sports.io/teams?league=39&season=2025",
        headers={"x-apisports-key": api_key, "User-Agent": "sports-analytics-capstone/1.0"},
    )
    teams = [
        item.get("team", {}).get("name")
        for item in data.get("response", [])
        if item.get("team", {}).get("name")
    ]
    return {"provider": "API-Football", "configured": True, "teams": teams}


def data_source_status() -> pd.DataFrame:
    rows = [
        {"source": "openfootball EPL Football.TXT", "status": "primary public cache", "credentials": "not required"},
        {"source": "football-data.co.uk CSV", "status": "secondary public cache", "credentials": "not required"},
    ]
    for loader in [fetch_football_data_org_teams, fetch_api_football_teams]:
        try:
            result = loader()
            rows.append(
                {
                    "source": result["provider"],
                    "status": "configured" if result["configured"] else "not configured",
                    "credentials": "environment variable",
                }
            )
        except Exception as exc:
            rows.append({"source": loader.__name__, "status": f"error: {exc}", "credentials": "environment variable"})
    return pd.DataFrame(rows)
