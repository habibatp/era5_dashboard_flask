from flask import Blueprint, request, jsonify
from services.sst_service import build_sst_dashboard
from services.cache_service import make_cache_key, load_cache, save_cache
from utils.ee_auth import init_earth_engine

sst_bp = Blueprint("sst_bp", __name__)

@sst_bp.route("/dashboard", methods=["POST"])
def sst_dashboard():
    init_earth_engine()

    payload = request.get_json(force=True)
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    geometry = payload.get("geometry")

    if not all([start_date, end_date, geometry]):
        return jsonify({"error": "start_date, end_date, geometry are required"}), 400

    cache_key = make_cache_key({
        "type": "sst",
        "start_date": start_date,
        "end_date": end_date,
        "geometry": geometry,
    })

    cached = load_cache(cache_key)
    if cached:
        cached["from_cache"] = True
        return jsonify(cached)

    try:
        result = build_sst_dashboard(start_date, end_date, geometry)
        result["from_cache"] = False
        save_cache(cache_key, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500