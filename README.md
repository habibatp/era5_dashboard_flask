# Environmental Data Dashboard & Wheat Yield Prediction

A modern web application built with Flask for visualizing environmental data, including ERA5 climate reanalysis, MODIS land data, and SST (Sea Surface Temperature).

This project also includes a complementary machine learning workflow for wheat yield prediction using FAOSTAT yield data and ERA5 surface meteorological variables.

The project evolved from a Streamlit prototype to a full-stack Flask application, providing better performance, a customizable user interface, modular architecture, and easier integration of data processing workflows.

---

## 🚀 Project Overview

This repository contains two complementary parts:

1. **Environmental Data Dashboard**
   - A Flask web dashboard for exploring environmental and climate data.
   - It supports ERA5, MODIS Land and SST data visualization.
   - It provides interactive time-series charts, tables, statistics and map-based selection.

2. **Wheat Yield Prediction**
   - A machine learning workflow for predicting wheat yield.
   - It combines FAOSTAT wheat yield data with ERA5 surface meteorological variables.
   - Several classical machine learning and deep learning models are tested and compared.

The main goal is to provide a practical tool for climate and environmental data exploration, while also demonstrating how meteorological data can be used in an agricultural application.

---

## 📊 Features

### 1. Multi-Source Environmental Data Integration

- **ERA5 Dashboard**
  - Retrieve, process and visualize ERA5 climate data directly from the Copernicus Climate Data Store (CDS API).
  - Supported variables include temperature, wind, pressure and precipitation.
  - Data can be extracted for a point location or averaged over a selected area.

- **MODIS Land Dashboard**
  - Analyze MODIS land-related variables.
  - Useful for exploring land surface environmental information.

- **SST Sea Dashboard**
  - Explore Sea Surface Temperature data.
  - Useful for coastal and marine environmental analysis.

---

### 2. Interactive Web Interface

- Modern and responsive frontend built with:
  - HTML5
  - CSS
  - Vanilla JavaScript
  - Chart.js
  - Leaflet.js

Main interface features:

- Select location by city, coordinates or map click.
- Choose environmental data source.
- Select variable and date range.
- Display time-series charts dynamically.
- View statistical summaries.
- View tabular data.
- Use zoom and pan on charts.

---

### 3. Intelligent Caching System

The application uses a local caching system to improve performance.

- Cached data are stored locally in Parquet format.
- Repeated queries are loaded from cache instead of being downloaded again.
- This reduces long API calls and improves user experience.
- Cache size management is included to avoid excessive storage usage.

---

### 4. Flexible Temporal Aggregation

The ERA5 module automatically adapts the temporal resolution according to the selected date range:

| Date Range | Mode | Time Step |
|-----------|------|-----------|
| ≤ 31 days | `raw_2h` | 2 hours |
| 31–92 days | `raw_4h` | 4 hours |
| 92–183 days | `raw_8h` | 8 hours |
| 183–365 days | `daily_summary` | Daily summary |
| > 365 days | `monthly_summary` | Monthly summary |

This adaptive logic helps maintain a balance between temporal detail, chart readability and processing time.

---

## 🌾 Wheat Yield Prediction Module

In addition to the environmental dashboard, this repository includes a machine learning workflow for wheat yield prediction.

### Objective

The goal of this module is to estimate wheat yield using annual climate indicators extracted from ERA5 surface variables and official wheat yield data from FAOSTAT.

This part is a complementary agricultural application of the climate data used in the project.

---

### Data Sources

#### 1. Wheat Yield Data

- Source: FAOSTAT, Food and Agriculture Organization.
- Crop: Wheat.
- Unit: kg/ha.
- Period: 1961–2024.
- Countries included:
  - Morocco
  - Algeria
  - Mauritania
  - Spain
  - Portugal
  - France

#### 2. ERA5 Surface Meteorological Data

- Source: ERA5 climate reanalysis.
- Period used: 1986–2025.
- Variables used:
  - `t2m`: 2-meter temperature
  - `u10`: 10-meter zonal wind component
  - `v10`: 10-meter meridional wind component
  - `msl`: mean sea level pressure
  - precipitation-related variables
  - derived wind speed variables

---

### Dataset Construction

The final dataset is created by merging FAOSTAT wheat yield data with annual ERA5 climate indicators.

For each country and each year, the following statistics are computed from ERA5 variables:

- annual mean
- annual standard deviation
- annual precipitation total
- derived wind speed mean
- derived wind speed standard deviation

The final merged dataset covers:

- Period: 1986–2024
- Number of countries: 6
- Number of observations: 234
- Target variable: wheat yield converted from kg/ha to t/ha

---

### Machine Learning Models Tested

Several regression models are trained and evaluated:

- Linear Regression
- Ridge Regression
- Lasso Regression
- Random Forest
- Extra Trees
- Gradient Boosting
- XGBoost
- LightGBM
- CatBoost

Deep learning models are also tested:

- Simple MLP
- Deep MLP
- 1D-CNN

---

### Evaluation Metrics

The models are evaluated using:

- MAE: Mean Absolute Error
- RMSE: Root Mean Squared Error
- R²: Coefficient of determination

The dataset is split chronologically:

- Training period: 1986–2018
- Test period: 2019–2024

This split simulates a realistic forecasting scenario where the model is trained on past years and evaluated on more recent years.

---

### Main Results

The best model among the tested approaches is **Ridge Regression**.

It achieves:

| Model | MAE (t/ha) | RMSE (t/ha) | R² |
|------|------------|-------------|----|
| Ridge | 0.402 | 0.549 | 0.917 |

These results show that a regularized linear model is well suited to this tabular dataset. This is mainly because the dataset is relatively small and contains aggregated annual climate indicators.

The deep learning models obtain lower performance, which is expected given the limited number of observations.

---

## 🛠️ Technology Stack

### Backend

- Python 3
- Flask

### Data Processing

- Pandas
- Xarray
- NumPy
- Scikit-learn

### External APIs

- CDS API (`cdsapi`) for ERA5 data retrieval

### Frontend

- HTML5
- CSS
- Vanilla JavaScript
- Chart.js
- Leaflet.js

### Machine Learning

- Scikit-learn
- XGBoost
- LightGBM
- CatBoost
- TensorFlow / Keras or PyTorch, depending on the deep learning notebook implementation

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/habibatp/era5_dashboard_flask.git
cd era5_dashboard_flask
```

### 2. Create and activate a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure CDS API credentials (for ERA5 data)

To access ERA5 climate data from the Copernicus Climate Data Store:

1. Create an account at [CDS](https://cds.climate.copernicus.eu/)
2. Go to your [user profile](https://cds.climate.copernicus.eu/profile) and copy your API credentials
3. Create a `.cdsapirc` file in your home directory:

**Windows:**
```
%USERPROFILE%\.cdsapirc
```

**macOS/Linux:**
```
~/.cdsapirc
```

Add the following content (replace with your actual UID and API key):
```
url: https://cds.climate.copernicus.eu/api/v2
key: {UID}:{API-KEY}
```

### 5. (Optional) Configure environment variables

Create a `.env` file in the project root for additional configuration:
```
FLASK_ENV=development
FLASK_DEBUG=True
DATA_CACHE_DIR=./data/cache
TEMP_DOWNLOAD_DIR=./temp_downloads
```

---

## 🚀 Usage

### Running the Flask Dashboard

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Features:

1. **Select Location**
   - Type a city name or coordinates
   - Click on the map to select a location
   - Adjust the selection area

2. **Choose Data Source**
   - ERA5 Climate Data
   - MODIS Land Data
   - Sea Surface Temperature (SST)

3. **Select Variable and Date Range**
   - Pick a meteorological or environmental variable
   - Choose start and end dates
   - Data resolution adapts automatically

4. **View Results**
   - Interactive time-series charts
   - Statistical summaries
   - Tabular data export
   - Download results as CSV

### Running the Wheat Yield Prediction Notebook

Open the Jupyter notebook:
```bash
jupyter notebook rendement_final.ipynb
```

This notebook contains:
- Data loading and preprocessing
- Feature engineering from ERA5 variables
- Model training and evaluation
- Visualization of results

---

## 📁 Project Structure

```
era5_dashboard_flask/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── config/                         # Configuration module
│   ├── __init__.py
│   └── settings.py                 # Application settings
│
├── core/                           # Core business logic
│   ├── __init__.py
│   ├── constants.py                # Constants and enumerations
│   ├── exceptions.py               # Custom exceptions
│   ├── models.py                   # Data models
│   └── validators.py               # Input validation
│
├── services/                       # Business logic services
│   ├── __init__.py
│   ├── era5_timeseries_service.py  # ERA5 data retrieval
│   ├── modis_service.py            # MODIS data handling
│   ├── sst_service.py              # Sea Surface Temperature service
│   ├── cache_service.py            # Caching layer
│   ├── aggregation_service.py      # Data aggregation
│   ├── export_service.py           # Data export utilities
│   ├── geo_service.py              # Geographic utilities
│   └── cds_client.py               # CDS API client
│
├── routes/                         # API endpoints
│   ├── era5_routes.py              # ERA5 endpoints
│   ├── modis_routes.py             # MODIS endpoints
│   └── sst_routes.py               # SST endpoints
│
├── plotting/                       # Visualization module
│   ├── __init__.py
│   ├── kpi_plotter.py              # KPI charts
│   ├── map_plotter.py              # Map visualizations
│   └── timeseries_plotter.py       # Time-series charts
│
├── ui/                             # UI components
│   ├── __init__.py
│   ├── controls_panel.py           # Control panel UI
│   ├── dashboard_view.py           # Main dashboard view
│   ├── data_table_view.py          # Data table display
│   ├── kpi_view.py                 # KPI view
│   └── map_selector.py             # Map selection interface
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── date_utils.py               # Date/time utilities
│   ├── file_utils.py               # File operations
│   ├── geometry_utils.py           # Geographic calculations
│   ├── logger.py                   # Logging configuration
│   ├── unit_utils.py               # Unit conversions
│   ├── cleanup.py                  # Cleanup utilities
│   └── ee_auth.py                  # Earth Engine authentication
│
├── templates/                      # HTML templates
│   ├── index.html                  # Landing page
│   ├── layout.html                 # Base layout
│   ├── dashboard.html              # Main dashboard template
│   └── pages/                      # Additional page templates
│
├── static/                         # Static assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│
├── data/
│   └── cache/                      # Cached data (Parquet format)
│
├── temp_downloads/                 # Temporary download directory
│
├── tests/                          # Test suite
│   ├── test_aggregation_service.py
│   ├── test_geo_service.py
│   └── test_validators.py
│
└── rendement_final.ipynb           # Wheat yield prediction notebook
```

---

## 🔧 Configuration

### CDS API Configuration

The application requires CDS API credentials for ERA5 data retrieval. Set up your credentials in `~/.cdsapirc`:

```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

### Application Settings

Edit `config/settings.py` to customize:
- Cache directory path
- Temporary downloads directory
- Default data aggregation modes
- API timeout values
- Log level and format

---

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Available tests:
- Aggregation service tests
- Geographic service tests
- Input validation tests

---

## 📊 Performance Optimization

### Caching Strategy

The application implements a multi-level caching system:

1. **Query Result Cache**: Stores processed data in Parquet format
2. **Cache Expiration**: Automatic cleanup of old cache files
3. **Cache Size Management**: Limits total cache size to prevent disk space issues

### Temporal Aggregation

The ERA5 module automatically selects the optimal time resolution:
- Short periods (≤31 days): 2-hour resolution
- Medium periods: 4-8 hour resolution
- Long periods: Daily or monthly aggregation

This improves performance and chart readability.

---

## 🌍 Data Sources

### ERA5 Climate Reanalysis
- **Provider**: Copernicus Climate Data Store
- **Variables**: Temperature, precipitation, wind, pressure
- **Resolution**: 0.25° × 0.25° grid
- **Temporal Coverage**: 1940–present (varies by variable)

### MODIS Land Data
- **Provider**: NASA EARTHDATA
- **Variables**: Land surface temperature, vegetation indices, etc.
- **Resolution**: 500m–1km
- **Temporal Coverage**: 2000–present

### Sea Surface Temperature (SST)
- **Provider**: Various oceanographic datasets
- **Temporal Coverage**: Recent historical data

---

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 👥 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact & Support

For questions, issues, or suggestions:
- Open an issue on [GitHub](https://github.com/habibatp/era5_dashboard_flask/issues)
- Check the [documentation](https://github.com/habibatp/era5_dashboard_flask)

---

## 🙏 Acknowledgments

- Copernicus Climate Data Store for ERA5 data
- NASA EARTHDATA for MODIS data
- FAO/FAOSTAT for wheat yield data
- Flask and open-source community