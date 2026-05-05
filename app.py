from flask import Flask, render_template
from config import Config
from config.settings import load_settings

from routes.era5_routes import era5_bp
from routes.modis_routes import modis_bp
from routes.sst_routes import sst_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Blueprints API
    app.register_blueprint(era5_bp)
    app.register_blueprint(modis_bp, url_prefix="/api/modis")
    app.register_blueprint(sst_bp, url_prefix="/api/sst")

    settings = load_settings()

    @app.route("/")
    def home():
        return render_template("pages/home.html", page_title="Dashboard des données")

    @app.route("/analysis/era5")
    def era5_page():
        cities = [
            {"name": city, "lat": coords[0], "lon": coords[1]}
            for city, coords in settings.cities.items()
        ]
        return render_template(
            "pages/era5.html",
            page_title="ERA5 Dashboard",
            cities=cities,
            surface_variables=settings.surface_variables,
            pressure_variables=settings.pressure_variables,
            pressure_levels=settings.pressure_levels,
            allowed_aggregations=settings.allowed_aggregations,
        )

    @app.route("/analysis/modis-land")
    def modis_land_page():
        return render_template(
            "pages/modis_land.html",
            page_title="MODIS - Land (Morocco / Spain)"
        )

    @app.route("/analysis/sst-sea")
    def sst_sea_page():
        return render_template(
            "pages/sst_sea.html",
            page_title="MODIS - Sea (Gibraltar Strait)"
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)