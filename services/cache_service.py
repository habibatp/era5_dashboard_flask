from __future__ import annotations

from pathlib import Path
import hashlib
import json


CACHE_DIR = Path("cache_data")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MAX_CACHE_SIZE_BYTES = int(1.5 * 1024 * 1024 * 1024)  # 1.5 GB


def _normalize_location(location):
    if isinstance(location, dict):
        return {
            "name": location.get("name", "point"),
            "lat": round(float(location["lat"]), 4),
            "lon": round(float(location["lon"]), 4),
        }

    return {
        "name": getattr(location, "location_name", "point"),
        "lat": round(float(location.latitude), 4),
        "lon": round(float(location.longitude), 4),
    }


def build_cache_key(selection: dict, mode: str) -> str:
    location = _normalize_location(selection["location"])

    payload = {
        "location_name": location["name"],
        "lat": location["lat"],
        "lon": location["lon"],
        "variable_type": selection["variable_type"],
        "variable": selection["variable"],
        "pressure_level": selection.get("pressure_level"),
        "start_date": str(selection["start_date"]),
        "end_date": str(selection["end_date"]),
        "aggregation": selection["aggregation"],
        "box_radius_deg": selection.get("box_radius_deg"),
        "mode": mode,
    }

    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def get_cache_path(cache_key: str) -> Path:
    return CACHE_DIR / f"{cache_key}.parquet"


def load_from_cache(cache_key: str):
    path = get_cache_path(cache_key)
    return path if path.exists() else None


def save_to_cache(df, cache_key: str) -> Path:
    path = get_cache_path(cache_key)
    df.to_parquet(path, index=False)
    enforce_cache_limit()
    return path


def cache_size_bytes() -> int:
    return sum(p.stat().st_size for p in CACHE_DIR.glob("*.parquet") if p.is_file())


def enforce_cache_limit() -> None:
    files = [p for p in CACHE_DIR.glob("*.parquet") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime)  # oldest first

    total = cache_size_bytes()

    while total > MAX_CACHE_SIZE_BYTES and files:
        oldest = files.pop(0)
        try:
            size = oldest.stat().st_size
            oldest.unlink()
            total -= size
        except FileNotFoundError:
            pass
import hashlib
import json
import time
from pathlib import Path
from flask import current_app

def _cache_path(key: str) -> Path:
    cache_dir = current_app.config["CACHE_DIR"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{key}.json"

def make_cache_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def load_cache(key: str):
    path = _cache_path(key)
    ttl = current_app.config["CACHE_TTL_SECONDS"]

    if not path.exists():
        return None

    age = time.time() - path.stat().st_mtime
    if age > ttl:
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(key: str, data: dict):
    path = _cache_path(key)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)