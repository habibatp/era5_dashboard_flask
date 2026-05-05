import ee
from utils.geometry_utils import geojson_to_ee_geometry

def build_sst_dashboard(start_date: str, end_date: str, geometry_geojson: dict):
    region = geojson_to_ee_geometry(geometry_geojson)

    col = (
        ee.ImageCollection("NOAA/CDR/OISST/V2_1")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select("sst")
    )

    def image_to_feature(img):
        # OISST est en Celsius * 0.01 dans EE ? On garde la valeur telle que fournie par le produit.
        # Si nécessaire, adapte ici selon tes tests.
        stats = img.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                reducer2=ee.Reducer.minMax(), sharedInputs=True
            ),
            geometry=region,
            scale=25000,
            maxPixels=1e13
        )

        return ee.Feature(None, {
            "date": ee.Date(img.get("system:time_start")).format("YYYY-MM-dd"),
            "mean": stats.get("sst_mean"),
            "min": stats.get("sst_min"),
            "max": stats.get("sst_max"),
        })

    fc = ee.FeatureCollection(col.map(image_to_feature))
    data = fc.getInfo()

    rows = []
    for feat in data["features"]:
        props = feat["properties"]
        rows.append({
            "date": props.get("date"),
            "mean": props.get("mean"),
            "min": props.get("min"),
            "max": props.get("max"),
        })

    clean_rows = [r for r in rows if r["mean"] is not None]

    if not clean_rows:
        return {
            "variable": "sst",
            "label": "Sea Surface Temperature",
            "series": [],
            "summary": {
                "count": 0,
                "mean": None,
                "min": None,
                "max": None,
            }
        }

    means = [r["mean"] for r in clean_rows]
    mins = [r["min"] for r in clean_rows if r["min"] is not None]
    maxs = [r["max"] for r in clean_rows if r["max"] is not None]

    return {
        "variable": "sst",
        "label": "Sea Surface Temperature",
        "series": clean_rows,
        "summary": {
            "count": len(clean_rows),
            "mean": sum(means) / len(means),
            "min": min(mins) if mins else None,
            "max": max(maxs) if maxs else None,
        }
    }