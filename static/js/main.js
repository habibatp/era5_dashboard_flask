window.selectedGeometry = null;
window.leafletMap = null;

function initMap() {
    const mapElement = document.getElementById("map");
    if (!mapElement) {
        return;
    }

    if (window.leafletMap) {
        window.leafletMap.remove();
        window.leafletMap = null;
    }

    const map = L.map("map").setView([31.5, -6.0], 5);
    window.leafletMap = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polyline: false,
            circle: false,
            circlemarker: false,
            marker: false
        }
    });

    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (event) {
        drawnItems.clearLayers();
        const layer = event.layer;
        drawnItems.addLayer(layer);

        const geojson = layer.toGeoJSON();
        window.selectedGeometry = geojson.geometry;

        const geometryInfo = document.getElementById("geometryInfo");
        if (geometryInfo) {
            geometryInfo.textContent = JSON.stringify(window.selectedGeometry, null, 2);
        }
    });

    map.on("click", function (e) {
        const latInput = document.getElementById("era5Latitude");
        const lonInput = document.getElementById("era5Longitude");

        if (latInput && lonInput) {
            latInput.value = e.latlng.lat.toFixed(4);
            lonInput.value = e.latlng.lng.toFixed(4);
        }
    });

    setTimeout(() => {
        map.invalidateSize();
    }, 300);
}

document.addEventListener("DOMContentLoaded", initMap);