const cities = window.APP_CONFIG.cities;
const surfaceVariables = window.APP_CONFIG.surfaceVariables;
const pressureVariables = window.APP_CONFIG.pressureVariables;

let mainMap;
let selectedMap;
let mapMarker = null;
let selectedMarker = null;
let mapClickLat = 31.6295;
let mapClickLon = -7.9811;

function initMainMap() {
    console.log("INIT MAIN MAP");

    mainMap = L.map("main-map").setView([33, -6], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
    }).addTo(mainMap);

    cities.forEach(c => {
        const marker = L.circleMarker([c.lat, c.lon], {
            radius: 5,
            color: "red",
            fillColor: "red",
            fillOpacity: 0.8
        }).addTo(mainMap);

        marker.bindPopup(c.name);

        marker.on("click", () => {
            document.querySelector('input[name="location_mode"][value="city"]').checked = true;
            onLocationModeChange();
            document.getElementById("city").value = c.name;
            updateSelectedLocation(c.name, c.lat, c.lon);
        });
    });

    mainMap.on("click", function (e) {
        mapClickLat = e.latlng.lat;
        mapClickLon = e.latlng.lng;

        if (mapMarker) {
            mainMap.removeLayer(mapMarker);
        }

        mapMarker = L.marker([mapClickLat, mapClickLon]).addTo(mainMap);

        const currentMode = document.querySelector('input[name="location_mode"]:checked').value;
        if (currentMode === "map") {
            updateSelectedLocation("Point from map", mapClickLat, mapClickLon);
        }
    });
}

function initSelectedMap(lat = 31.6295, lon = -7.9811, name = "Marrakech") {
    selectedMap = L.map("selected-map").setView([lat, lon], 7);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
    }).addTo(selectedMap);

    selectedMarker = L.marker([lat, lon]).addTo(selectedMap).bindPopup(name).openPopup();
}

function updateSelectedMap(lat, lon, name) {
    if (!selectedMap) return;

    selectedMap.setView([lat, lon], 7);

    if (selectedMarker) {
        selectedMap.removeLayer(selectedMarker);
    }

    selectedMarker = L.marker([lat, lon]).addTo(selectedMap).bindPopup(name).openPopup();

    setTimeout(() => selectedMap.invalidateSize(), 100);
}

function updateSelectedLocation(name, lat, lon) {
    const nameEl = document.getElementById("selected-name");
    const latEl = document.getElementById("selected-lat");
    const lonEl = document.getElementById("selected-lon");

    if (nameEl) nameEl.textContent = name;
    if (latEl) latEl.textContent = Number(lat).toFixed(4);
    if (lonEl) lonEl.textContent = Number(lon).toFixed(4);

    const latInput = document.getElementById("lat");
    const lonInput = document.getElementById("lon");

    if (latInput) latInput.value = Number(lat).toFixed(4);
    if (lonInput) lonInput.value = Number(lon).toFixed(4);

    updateSelectedMap(lat, lon, name);
}

function onLocationModeChange() {
    const mode = document.querySelector('input[name="location_mode"]:checked').value;
    const cityBlock = document.getElementById("city-block");
    const coordsBlock = document.getElementById("coords-block");

    if (cityBlock) cityBlock.classList.add("hidden");
    if (coordsBlock) coordsBlock.classList.add("hidden");

    if (mode === "city") {
        if (cityBlock) cityBlock.classList.remove("hidden");
        const cityName = document.getElementById("city").value;
        const c = cities.find(x => x.name === cityName);
        if (c) updateSelectedLocation(c.name, c.lat, c.lon);
    } else {
        if (coordsBlock) coordsBlock.classList.remove("hidden");
        const lat = parseFloat(document.getElementById("lat").value);
        const lon = parseFloat(document.getElementById("lon").value);
        updateSelectedLocation(mode === "map" ? "Point from map" : "Custom point", lat, lon);
    }
}

function populateVariables() {
    const variableType = document.querySelector('input[name="variable_type"]:checked').value;
    const variableSelect = document.getElementById("variable");
    const pressureBlock = document.getElementById("pressure-block");

    if (!variableSelect) return;

    variableSelect.innerHTML = "";

    if (variableType === "surface") {
        Object.entries(surfaceVariables).forEach(([key, label]) => {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = `${key} — ${label}`;
            variableSelect.appendChild(opt);
        });
        if (pressureBlock) pressureBlock.classList.add("hidden");
    } else {
        Object.entries(pressureVariables).forEach(([key, label]) => {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = `${key} — ${label}`;
            variableSelect.appendChild(opt);
        });
        if (pressureBlock) pressureBlock.classList.remove("hidden");
    }
}

function renderSummary(result, payload) {
    const summary = document.getElementById("summary");
    if (!summary) return;

    summary.innerHTML = `
        <p><strong>Location:</strong> ${result.location_name}</p>
        <p><strong>Variable:</strong> ${result.variable}</p>
        <p><strong>Date range:</strong> ${payload.start_date} → ${payload.end_date}</p>
        <p><strong>Aggregation:</strong> ${result.aggregation}</p>
        <p><strong>Source:</strong> ${result.source}</p>
        <p><strong>Mode:</strong> ${result.mode}</p>
    `;
}

function renderKpis(kpis, unit) {
    const container = document.getElementById("kpis");
    if (!container) return;

    container.innerHTML = `
        <div class="kpi-card"><div class="label">Minimum</div><div class="value">${formatValue(kpis.min)} ${unit}</div></div>
        <div class="kpi-card"><div class="label">Maximum</div><div class="value">${formatValue(kpis.max)} ${unit}</div></div>
        <div class="kpi-card"><div class="label">Mean</div><div class="value">${formatValue(kpis.mean)} ${unit}</div></div>
        <div class="kpi-card"><div class="label">Std</div><div class="value">${formatValue(kpis.std)} ${unit}</div></div>
        <div class="kpi-card"><div class="label">Count</div><div class="value">${kpis.count}</div></div>
    `;
}

function renderTable(rows, mode) {
    const tbody = document.querySelector("#data-table tbody");
    const thead = document.querySelector("#data-table thead");
    if (!tbody || !thead) return;

    tbody.innerHTML = "";

    if (!rows.length) return;

    if (mode === "hourly_24h" || mode === "hourly_12h") {
        thead.innerHTML = `
            <tr>
                <th>time</th>
                <th>value</th>
            </tr>
        `;

        rows.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${r.time}</td><td>${formatValue(r.value)}</td>`;
            tbody.appendChild(tr);
        });
    } else {
        thead.innerHTML = `
            <tr>
                <th>date</th>
                <th>min</th>
                <th>max</th>
                <th>mean</th>
            </tr>
        `;

        rows.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.time}</td>
                <td>${formatValue(r.min)}</td>
                <td>${formatValue(r.max)}</td>
                <td>${formatValue(r.mean)}</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function renderChart(result) {
    const chartTitle = document.getElementById("chart-title");
    if (chartTitle) {
        chartTitle.textContent = `${result.variable} evolution — ${result.location_name}`;
    }

    let traces = [];

    if (result.mode === "hourly_24h" || result.mode === "hourly_12h") {
        const x = result.data.map(d => d.time);
        const y = result.data.map(d => d.value);

        traces = [{
            x: x,
            y: y,
            mode: "lines",
            type: "scatter",
            name: result.mode === "hourly_24h" ? "Hourly value (24h)" : "Hourly value (12h)",
            line: { width: 2 }
        }];
    } else {
        const x = result.data.map(d => d.time);
        const yMin = result.data.map(d => d.min);
        const yMax = result.data.map(d => d.max);
        const yMean = result.data.map(d => d.mean);

        traces = [
            {
                x: x,
                y: yMin,
                mode: "lines",
                name: "Daily min",
                line: { width: 2 }
            },
            {
                x: x,
                y: yMax,
                mode: "lines",
                name: "Daily max",
                line: { width: 2 }
            },
            {
                x: x,
                y: yMean,
                mode: "lines",
                name: "Daily mean",
                line: { width: 3 }
            }
        ];
    }

    Plotly.newPlot("chart", traces, {
        template: "plotly_dark",
        paper_bgcolor: "#111827",
        plot_bgcolor: "#111827",
        font: { color: "#f3f4f6" },
        margin: { t: 20, r: 20, b: 60, l: 60 },
        xaxis: { title: "Time" },
        yaxis: { title: result.unit }
    }, { responsive: true });
}

async function loadData() {
    const locationMode = document.querySelector('input[name="location_mode"]:checked').value;
    const variableType = document.querySelector('input[name="variable_type"]:checked').value;

    let payload = {
        location_mode: locationMode,
        variable_type: variableType,
        variable: document.getElementById("variable").value,
        pressure_level: variableType === "pressure" ? parseInt(document.getElementById("pressure_level").value) : null,
        start_date: document.getElementById("start_date").value,
        end_date: document.getElementById("end_date").value,
        aggregation: document.getElementById("aggregation").value,
        box_radius_deg: parseFloat(document.getElementById("box_radius_deg").value)
    };

    if (locationMode === "city") {
        payload.city = document.getElementById("city").value;
    } else if (locationMode === "coords") {
        payload.lat = parseFloat(document.getElementById("lat").value);
        payload.lon = parseFloat(document.getElementById("lon").value);
    } else {
        payload.lat = mapClickLat;
        payload.lon = mapClickLon;
    }

    const btn = document.getElementById("load-btn");
    if (btn) {
        btn.disabled = true;
        btn.textContent = "Loading...";
    }

    try {
        const res = await fetch("/api/timeseries", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await res.json();

        if (result.error) {
            alert(result.error);
            return;
        }

        updateSelectedMap(result.latitude, result.longitude, result.location_name);
        renderSummary(result, payload);
        renderKpis(result.kpis, result.unit);
        renderChart(result);
        renderTable(result.data, result.mode);
    } catch (err) {
        alert("Erreur lors du chargement des données.");
        console.error(err);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = "Load data";
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("PAGE LOADED");

    initMainMap();
    initSelectedMap();
    populateVariables();

    setTimeout(() => {
        if (mainMap) mainMap.invalidateSize();
        if (selectedMap) selectedMap.invalidateSize();
    }, 300);

    document.querySelectorAll('input[name="location_mode"]').forEach(el => {
        el.addEventListener("change", onLocationModeChange);
    });

    document.querySelectorAll('input[name="variable_type"]').forEach(el => {
        el.addEventListener("change", populateVariables);
    });

    const cityEl = document.getElementById("city");
    if (cityEl) {
        cityEl.addEventListener("change", () => {
            const cityName = cityEl.value;
            const c = cities.find(x => x.name === cityName);
            if (c) updateSelectedLocation(c.name, c.lat, c.lon);
        });
    }

    const latEl = document.getElementById("lat");
    const lonEl = document.getElementById("lon");

    if (latEl) {
        latEl.addEventListener("input", () => {
            const lat = parseFloat(latEl.value);
            const lon = parseFloat(lonEl.value);
            updateSelectedLocation("Custom point", lat, lon);
        });
    }

    if (lonEl) {
        lonEl.addEventListener("input", () => {
            const lat = parseFloat(latEl.value);
            const lon = parseFloat(lonEl.value);
            updateSelectedLocation("Custom point", lat, lon);
        });
    }

    const radiusEl = document.getElementById("box_radius_deg");
    if (radiusEl) {
        radiusEl.addEventListener("input", (e) => {
            document.getElementById("radius-value").textContent = e.target.value;
        });
    }

    const loadBtn = document.getElementById("load-btn");
    if (loadBtn) {
        loadBtn.addEventListener("click", loadData);
    }

    const c = cities.find(x => x.name === "Marrakech") || cities[0];
    if (c) updateSelectedLocation(c.name, c.lat, c.lon);
});
function formatValue(v) {
    const num = Number(v);

    if (!Number.isFinite(num)) return "NaN";

    const absVal = Math.abs(num);

    if (absVal === 0) return "0";
    if (absVal < 0.01) return num.toExponential(3);   // ex: 2.547e-3
    if (absVal < 1) return num.toFixed(6);
    return num.toFixed(3);
}