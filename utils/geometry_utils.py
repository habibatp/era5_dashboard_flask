import ee

def geojson_to_ee_geometry(geojson: dict) -> ee.Geometry:
    """
    Convertit un GeoJSON simple en ee.Geometry.
    Supporte Polygon, MultiPolygon, Rectangle, Feature, FeatureCollection.
    """
    if not geojson:
        raise ValueError("Geometry is required.")

    geo_type = geojson.get("type")

    if geo_type == "Feature":
        return geojson_to_ee_geometry(geojson["geometry"])

    if geo_type == "FeatureCollection":
        first_feature = geojson["features"][0]
        return geojson_to_ee_geometry(first_feature["geometry"])

    if geo_type == "Polygon":
        return ee.Geometry.Polygon(geojson["coordinates"])

    if geo_type == "MultiPolygon":
        return ee.Geometry.MultiPolygon(geojson["coordinates"])

    if geo_type == "Rectangle":
        coords = geojson["coordinates"]
        return ee.Geometry.Rectangle(coords)

    raise ValueError(f"Unsupported geometry type: {geo_type}")