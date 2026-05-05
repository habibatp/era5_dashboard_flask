let era5Chart = null;
let era5AbortController = null;
let era5Loading = false;

function updateEra5ModeUI() {
    const type = document.querySelector('input[name="era5VariableType"]:checked')?.value || "surface";

    const surfaceSelect = document.getElementById("era5SurfaceVariable");
    const pressureSelect = document.getElementById("era5PressureVariable");
    const pressureLevel = document.getElementById("era5PressureLevel");

    if (!surfaceSelect || !pressureSelect || !pressureLevel) {
        console.error("ERA5 UI elements not found for variable type switch.");
        return;
    }

    if (type === "surface") {
        surfaceSelect.style.display = "block";
        pressureSelect.style.display = "none";
        pressureLevel.style.display = "none";
    } else {
        surfaceSelect.style.display = "none";
        pressureSelect.style.display = "block";
        pressureLevel.style.display = "block";
    }
}

function updateLocationModeUI() {
    const mode = document.querySelector('input[name="locationMode"]:checked')?.value || "city";
    const cityBlock = document.getElementById("cityModeBlock");
    const coordsBlock = document.getElementById("coordsModeBlock");

    if (!cityBlock || !coordsBlock) {
        console.error("Location mode blocks not found.");
        return;
    }

    if (mode === "city") {
        cityBlock.style.display = "block";
        coordsBlock.style.display = "none";
    } else {
        cityBlock.style.display = "none";
        coordsBlock.style.display = "block";
    }
}

function updateSelectedZoneCard(name, lat, lon) {
    const nameEl = document.getElementById("selectedName");
    const latEl = document.getElementById("selectedLat");
    const lonEl = document.getElementById("selectedLon");

    if (nameEl) nameEl.textContent = name ?? "-";
    if (latEl) latEl.textContent = lat ?? "-";
    if (lonEl) lonEl.textContent = lon ?? "-";
}

function bindEra5Controls() {
    console.log("bindEra5Controls called");

    const radios = document.querySelectorAll('input[name="era5VariableType"]');
    radios.forEach(r => r.addEventListener("change", updateEra5ModeUI));

    const locationModeRadios = document.querySelectorAll('input[name="locationMode"]');
    locationModeRadios.forEach(r => r.addEventListener("change", updateLocationModeUI));

    const citySelect = document.getElementById("era5City");
    if (citySelect) {
        citySelect.addEventListener("change", function () {
            const [lat, lon, name] = this.value.split(",");
            const latInput = document.getElementById("era5Latitude");
            const lonInput = document.getElementById("era5Longitude");
            const nameInput = document.getElementById("era5LocationName");

            if (latInput) latInput.value = lat;
            if (lonInput) lonInput.value = lon;
            if (nameInput) nameInput.value = name;

            updateSelectedZoneCard(name, lat, lon);
        });

        const [lat, lon, name] = citySelect.value.split(",");
        const latInput = document.getElementById("era5Latitude");
        const lonInput = document.getElementById("era5Longitude");
        const nameInput = document.getElementById("era5LocationName");

        if (latInput) latInput.value = lat;
        if (lonInput) lonInput.value = lon;
        if (nameInput) nameInput.value = name;

        updateSelectedZoneCard(name, lat, lon);
    }

    const boxRadius = document.getElementById("era5BoxRadius");
    const boxRadiusValue = document.getElementById("era5BoxRadiusValue");
    if (boxRadius && boxRadiusValue) {
        boxRadius.addEventListener("input", function () {
            boxRadiusValue.textContent = this.value;
        });
    }

    updateEra5ModeUI();
    updateLocationModeUI();
}

function setEra5LoadingState(isLoading) {
    era5Loading = isLoading;

    const btn = document.getElementById("era5LoadBtn");
    const loading = document.getElementById("era5Loading");

    if (btn) {
        btn.disabled = isLoading;
        btn.textContent = isLoading ? "Loading..." : "Load data";
    }

    if (loading) {
        loading.style.display = isLoading ? "block" : "none";
    }
}

function renderEra5Table(data) {
    console.log("renderEra5Table called", data);

    const head = document.getElementById("era5TableHead");
    const body = document.getElementById("era5TableBody");

    if (!head || !body) {
        console.error("ERA5 table elements not found.");
        return;
    }

    if (data.mode === "raw") {
        head.innerHTML = `
            <th>time</th>
            <th>value</th>
        `;

        body.innerHTML = data.series.map(item => `
            <tr>
                <td>${item.time}</td>
                <td>${item.value ?? ""}</td>
            </tr>
        `).join("");
    } else {
        head.innerHTML = `
            <th>time</th>
            <th>mean</th>
            <th>min</th>
            <th>max</th>
        `;

        body.innerHTML = data.series.map(item => `
            <tr>
                <td>${item.time}</td>
                <td>${item.mean ?? ""}</td>
                <td>${item.min ?? ""}</td>
                <td>${item.max ?? ""}</td>
            </tr>
        `).join("");
    }
}
function normalizeEra5Response(response, variable, locationName) {
    const strategy = response.strategy || {};
    const rows = response.data || [];

    const firstRow = rows[0] || {};
    const valueColumns = Object.keys(firstRow).filter(k =>
        !["time", "number", "expver", "latitude", "longitude"].includes(k)
    );

    let mode = strategy.mode || "local_6h";

    let series = [];

    if (
        mode === "local_6h" ||
        mode === "local_12h" ||
        mode === "api_hourly_2h"
    ) {
        const valueCol = valueColumns.includes(variable) ? variable : valueColumns[0];

        series = rows.map(row => ({
            time: row.time,
            value: row[valueCol]
        }));

        mode = "raw";
    } else {
        const meanCol = valueColumns.find(c => c.includes("_mean"));
        const minCol = valueColumns.find(c => c.includes("_min"));
        const maxCol = valueColumns.find(c => c.includes("_max"));

        series = rows.map(row => ({
            time: row.time,
            mean: row[meanCol],
            min: row[minCol],
            max: row[maxCol]
        }));
    }

    return {
        variable: variable,
        unit: response.unit || "",
        location_name: locationName,
        source: strategy.source || "-",
        mode: mode,
        series: series
    };
}

function renderEra5Chart(data) {
    console.log("renderEra5Chart called", data);

    const canvas = document.getElementById("era5Chart");
    if (!canvas) {
        throw new Error("Canvas #era5Chart introuvable.");
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
        throw new Error("Impossible d'obtenir le contexte 2D.");
    }

    if (!data || !Array.isArray(data.series)) {
        throw new Error("Réponse invalide : data.series manquant.");
    }

    if (era5Chart) {
        era5Chart.destroy();
    }

    const labels = data.series.map(item => item.time);
    let datasets = [];

    if (data.mode === "raw") {
        datasets = [
            {
                label: `${data.variable} (${data.unit})`,
                data: data.series.map(item => item.value ?? null),
                borderWidth: 2,
                tension: 0.15,
                pointRadius: 2,
                pointHoverRadius: 6,
                fill: false
            }
        ];
    } else {
        datasets = [
            {
                label: `Mean (${data.unit})`,
                data: data.series.map(item => item.mean ?? null),
                borderWidth: 2,
                tension: 0.15,
                pointRadius: 2,
                pointHoverRadius: 6,
                fill: false
            },
            {
                label: `Min (${data.unit})`,
                data: data.series.map(item => item.min ?? null),
                borderWidth: 2,
                tension: 0.15,
                pointRadius: 2,
                pointHoverRadius: 6,
                fill: false
            },
            {
                label: `Max (${data.unit})`,
                data: data.series.map(item => item.max ?? null),
                borderWidth: 2,
                tension: 0.15,
                pointRadius: 2,
                pointHoverRadius: 6,
                fill: false
            }
        ];
    }

    era5Chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "nearest",
                intersect: false
            },
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        title: function (context) {
                            return context[0].label;
                        },
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y}`;
                        }
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: "x"
                    },
                    zoom: {
                        wheel: {
                            enabled: true
                        },
                        pinch: {
                            enabled: true
                        },
                        drag: {
                            enabled: true,
                            backgroundColor: "rgba(37, 99, 235, 0.15)"
                        },
                        mode: "x"
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 12
                    }
                },
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    const summary = document.getElementById("era5Summary");
    if (summary) {
        summary.innerHTML = `
            <p><strong>Location:</strong> ${data.location_name ?? "-"}</p>
            <p><strong>Variable:</strong> ${data.variable ?? "-"}</p>
            <p><strong>Unit:</strong> ${data.unit ?? "-"}</p>
            <p><strong>Mode:</strong> ${data.mode ?? "-"}</p>
            <p><strong>Source:</strong> ${data.source ?? "-"}</p>
            <p><strong>Points:</strong> ${data.series.length}</p>
            <button class="primary-btn" style="margin-top:10px;" onclick="resetEra5Zoom()">Reset zoom</button>
        `;
    }

    renderEra5Table(data);
}

async function fetchEra5Dashboard() {
    console.log("fetchEra5Dashboard called");

    if (era5Loading) {
        console.log("Already loading, request ignored.");
        return;
    }

    try {
        setEra5LoadingState(true);

        if (era5AbortController) {
            era5AbortController.abort();
        }
        era5AbortController = new AbortController();

        const variableType = document.querySelector('input[name="era5VariableType"]:checked')?.value || "surface";
        const locationMode = document.querySelector('input[name="locationMode"]:checked')?.value || "city";

        let lat, lon, name;

        if (locationMode === "city") {
            const cityEl = document.getElementById("era5City");
            if (!cityEl) {
                throw new Error("Select #era5City introuvable.");
            }
            const cityRaw = cityEl.value.split(",");
            lat = parseFloat(cityRaw[0]);
            lon = parseFloat(cityRaw[1]);
            name = cityRaw[2];
        } else {
            const latEl = document.getElementById("era5Latitude");
            const lonEl = document.getElementById("era5Longitude");
            const nameEl = document.getElementById("era5LocationName");

            if (!latEl || !lonEl) {
                throw new Error("Champs latitude/longitude manquants.");
            }

            lat = parseFloat(latEl.value.replace(",", "."));
            lon = parseFloat(lonEl.value.replace(",", "."));
            name = nameEl ? nameEl.value : "Selected point";
        }
        if (isNaN(lat) || isNaN(lon)) {
            alert("Veuillez sélectionner une position valide sur la carte ou entrer des coordonnées.");
            return;
        }
        updateSelectedZoneCard(name, lat, lon);

        const variable = variableType === "surface"
            ? document.getElementById("era5SurfaceVariable")?.value
            : document.getElementById("era5PressureVariable")?.value;

        if (!variable) {
            throw new Error("Aucune variable sélectionnée.");
        }

        const payload = {
            data_type: variableType,
            variable: variable,
            start_date: document.getElementById("era5StartDate")?.value,
            end_date: document.getElementById("era5EndDate")?.value,
            lat: lat,
            lon: lon,
            location_name: name,
            level: variableType === "pressure"
                ? parseInt(document.getElementById("era5PressureLevel")?.value)
                : null
        };

        if (variableType === "pressure") {
            payload.pressure_level = parseInt(document.getElementById("era5PressureLevel")?.value);
        }

        console.log("ERA5 payload =", payload);

        const response = await fetch("/api/timeseries", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload),
            signal: era5AbortController.signal
        });


        const data = await response.json();
        console.log("ERA5 response =", data);

        if (!response.ok) {
            throw new Error(data.error || "Erreur lors du chargement des données.");
        }

        const normalizedData = normalizeEra5Response(data, variable, name);
        renderEra5Chart(normalizedData);


    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("ERA5 FRONTEND ERROR =", error);
            alert(error.message || "Erreur lors du chargement des données.");
        }
    } finally {
        setEra5LoadingState(false);
    }
}
function resetEra5Zoom() {
    if (era5Chart) {
        era5Chart.resetZoom();
    }
}

document.addEventListener("DOMContentLoaded", bindEra5Controls);