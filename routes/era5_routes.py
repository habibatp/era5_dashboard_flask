from flask import Blueprint, request, jsonify, render_template
from services.era5_timeseries_service import get_era5_timeseries
from config.settings import load_settings
import math


era5_bp = Blueprint("era5", __name__)

@era5_bp.route("/analysis/era5")
def era5_page():
    settings = load_settings()

    return render_template(
        "pages/era5.html",
        cities=settings.cities,
        surface_variables=settings.surface_variables,
        pressure_variables=settings.pressure_variables,
        pressure_levels=settings.pressure_levels,
        allowed_aggregations=settings.allowed_aggregations,
        min_available_date=settings.min_available_date,
        max_available_date=settings.max_available_date,
    )


@era5_bp.route("/api/timeseries", methods=["POST"])
def api_timeseries():
    try:
        payload = request.get_json()

        data_type = payload.get("data_type") or payload.get("variable_type") or "surface"
        variable = payload.get("variable")
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")

        lat = payload.get("lat")
        lon = payload.get("lon")
        level = payload.get("level")

        lat = float(lat) if lat not in [None, ""] else None
        lon = float(lon) if lon not in [None, ""] else None
        level = int(level) if level not in [None, ""] else None
        if lat is None or lon is None:
            return jsonify({
                "error": "Latitude et longitude sont obligatoires. Sélectionnez une ville, entrez des coordonnées ou cliquez sur la carte."
            }), 400
        
        result = get_era5_timeseries(
            data_type=data_type,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            lat=lat,
            lon=lon,
            level=level
        )

        return jsonify(result)

    except Exception as e:
         import traceback
         traceback.print_exc()
         return jsonify({"error": str(e)}), 500
         
      