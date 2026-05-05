# Environmental Data Dashboard (Flask)

A modern web application built with Flask for visualizing environmental data, including ERA5 climate reanalysis, MODIS land data, and SST (Sea Surface Temperature). 

This project evolved from a Streamlit application to a full-stack Flask application, providing better performance, a highly customizable user interface, and modular architecture.

## 🚀 Features

- **Multi-Source Data Integration**:
  - **ERA5 Dashboard**: Retrieve, process, and visualize ERA5 climate data (temperature, wind, pressure, precipitation) directly from the Copernicus Climate Data Store (CDS API).
  - **MODIS Land**: Dashboard for analyzing MODIS land variables.
  - **SST Sea**: Dashboard for exploring Sea Surface Temperature data.
- **Dynamic Frontend**: Modern and responsive user interface built with Vanilla JS, HTML, and CSS.
- **Interactive Visualizations**: Time-series charts generated dynamically with Chart.js, featuring zoom and pan capabilities.
- **Intelligent Caching System**: Fast data retrieval via local Parquet-based caching to avoid redundant, time-consuming API requests to CDS, with automatic size limit management.
- **Flexible Data Aggregation**: Analyze data at multiple resolutions: raw (2h, 4h, 8h), daily summaries, or monthly summaries based on your selected date range.

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Data Processing**: Pandas, Xarray
- **External APIs**: CDS API (`cdsapi`)
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript, Chart.js, Leaflet.js (for maps)

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/habibatp/era5_dashboard_flask.git
   cd era5_dashboard_flask
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure CDS API:**
   To retrieve ERA5 data, you must have a `.cdsapirc` file in your home directory (`~/.cdsapirc` on Linux/Mac or `C:\Users\YourUsername\.cdsapirc` on Windows) with your Copernicus API credentials.

   Format of `.cdsapirc`:
   ```text
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR_UID:YOUR_API_KEY
   ```

## ⚙️ Usage

Start the Flask development server:
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`.

## 📂 Project Structure

- `app.py`: Main Flask application and route definitions.
- `routes/`: Blueprint modules for different dashboards (ERA5, MODIS, SST).
- `services/`: Core logic for data retrieval, caching, and processing (`era5_timeseries_service.py`, `cache_service.py`, etc.).
- `templates/`: HTML templates.
- `static/`: Static assets (CSS, JS, images).
- `cache_data/`: Local storage for cached data files (Parquet format) to speed up repeated queries.
- `temp_downloads/`: Temporary directory for downloaded NetCDF files.

## 📝 License

This project is licensed under the MIT License.