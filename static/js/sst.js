let sstChart = null;

function renderSstChart(data) {
    const canvas = document.getElementById("sstChart");
    const ctx = canvas.getContext("2d");

    const labels = data.series.map(item => item.date);
    const values = data.series.map(item => item.mean);

    if (sstChart) {
        sstChart.destroy();
    }

    sstChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                borderWidth: 2,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    document.getElementById("sstSummary").innerHTML = `
        <p><strong>Count:</strong> ${data.summary.count ?? "-"}</p>
        <p><strong>Mean:</strong> ${data.summary.mean ?? "-"}</p>
        <p><strong>Min:</strong> ${data.summary.min ?? "-"}</p>
        <p><strong>Max:</strong> ${data.summary.max ?? "-"}</p>
        <p><strong>Cache:</strong> ${data.from_cache ? "Yes" : "No"}</p>
    `;
}

async function fetchSstDashboard() {
    const geometry = window.selectedGeometry;
    if (!geometry) {
        alert("Please draw a sea region on the map first.");
        return;
    }

    const payload = {
        start_date: document.getElementById("sstStartDate").value,
        end_date: document.getElementById("sstEndDate").value,
        geometry: geometry
    };

    const response = await fetch("/api/sst/dashboard", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "SST request failed.");
        return;
    }

    renderSstChart(data);
}