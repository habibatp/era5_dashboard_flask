import ee
from utils.geometry_utils import geojson_to_ee_geometry

MODIS_VARIABLES = {
    "terra_lst_day": {
        "collection": "MODIS/061/MOD11A2",
        "band": "LST_Day_1km",
        "scale_factor": 0.02,
        "offset": -273.15,
        "scale": 1000,
        "qa_band": "QC_Day",
        "label": "Terra LST Day (°C)",
    },
    "terra_lst_night": {
        "collection": "MODIS/061/MOD11A2",
        "band": "LST_Night_1km",
        "scale_factor": 0.02,
        "offset": -273.15,
        "scale": 1000,
        "qa_band": "QC_Night",
        "label": "Terra LST Night (°C)",
    },
    "terra_lst_qa_day": {
        "collection": "MODIS/061/MOD11A2",
        "band": "QC_Day",
        "scale_factor": 1.0,
        "offset": 0.0,
        "scale": 1000,
        "qa_band": None,
        "label": "Terra LST QA Day",
    },
    "terra_lst_qa_night": {
        "collection": "MODIS/061/MOD11A2",
        "band": "QC_Night",
        "scale_factor": 1.0,
        "offset": 0.0,
        "scale": 1000,
        "qa_band": None,
        "label": "Terra LST QA Night",
    },
    "terra_ndvi": {
        "collection": "MODIS/061/MOD13Q1",
        "band": "NDVI",
        "scale_factor": 0.0001,
        "offset": 0.0,
        "scale": 250,
        "qa_band": "SummaryQA",
        "label": "Terra NDVI",
    },
    "terra_ndvi_qa": {
        "collection": "MODIS/061/MOD13Q1",
        "band": "SummaryQA",
        "scale_factor": 1.0,
        "offset": 0.0,
        "scale": 250,
        "qa_band": None,
        "label": "Terra NDVI QA",
    },
    "aqua_lst_day": {
        "collection": "MODIS/061/MYD11A2",
        "band": "LST_Day_1km",
        "scale_factor": 0.02,
        "offset": -273.15,
        "scale": 1000,
        "qa_band": "QC_Day",
        "label": "Aqua LST Day (°C)",
    },
    "aqua_lst_night": {
        "collection": "MODIS/061/MYD11A2",
        "band": "LST_Night_1km",
        "scale_factor": 0.02,
        "offset": -273.15,
        "scale": 1000,
        "qa_band": "QC_Night",
        "label": "Aqua LST Night (°C)",
    },
    "aqua_lst_qa_day": {
        "collection": "MODIS/061/MYD11A2",
        "band": "QC_Day",
        "scale_factor": 1.0,
        "offset": 0.0,
        "scale": 1000,
        "qa_band": None,
        "label": "Aqua LST QA Day",
    },
    "aqua_lst_qa_night": {
        "collection": "MODIS/061/MYD11A2",
        "band": "QC_Night",
        "scale_factor": 1.0,
        "offset": 0.0,
        "scale": 1000,
        "qa_band": None,
        "label": "Aqua LST QA Night",
    },
    "aqua_ndvi": {
        "collection": "MODIS/061/MYD13Q1",
        "band": "NDVI",
        "scale_factor": 0.0001,
        "offset": 0.0,
        "scale": 250,
        "qa_band": "SummaryQA",
        "label": "Aqua NDVI",
    },
    "aqua_ndvi_qa": {
        "collection": "MODIS/061/MYD13Q1",
        "band": "SummaryQA",
        "scale_factor": 1.0,
        "offset": 0.0,
        "scale": 250,
        "qa_band": None,
        "label": "Aqua NDVI QA",
    },
}

def _apply_transform(img, band, scale_factor, offset):
    return img.select(band).multiply(scale_factor).add(offset).rename("value")

def build_modis_dashboard(variable: str, start_date: str, end_date: str, geometry_geojson: dict):
    if variable not in MODIS_VARIABLES:
        raise ValueError(f"Unsupported MODIS variable: {variable}")

    cfg = MODIS_VARIABLES[variable]
    region = geojson_to_ee_geometry(geometry_geojson)

    col = (
        ee.ImageCollection(cfg["collection"])
        .filterDate(start_date, end_date)
        .filterBounds(region)
    )

    def image_to_feature(img):
        processed = _apply_transform(img, cfg["band"], cfg["scale_factor"], cfg["offset"])

        stats = processed.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                reducer2=ee.Reducer.minMax(), sharedInputs=True
            ),
            geometry=region,
            scale=cfg["scale"],
            maxPixels=1e13
        )

        return ee.Feature(None, {
            "date": ee.Date(img.get("system:time_start")).format("YYYY-MM-dd"),
            "mean": stats.get("value_mean"),
            "min": stats.get("value_min"),
            "max": stats.get("value_max"),
        })

    features = col.map(image_to_feature)
    fc = ee.FeatureCollection(features)
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
            "variable": variable,
            "label": cfg["label"],
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
        "variable": variable,
        "label": cfg["label"],
        "series": clean_rows,
        "summary": {
            "count": len(clean_rows),
            "mean": sum(means) / len(means) if means else None,
            "min": min(mins) if mins else None,
            "max": max(maxs) if maxs else None,
        }
    }