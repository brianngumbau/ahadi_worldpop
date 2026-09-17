# Kenya Subnational Population Demographics & Public Health Analytics

A reproducible geospatial data pipeline and interactive dashboard analyzing WorldPop 2021–2025 age- and sex-structured population projections across Kenya's 47 counties.

## System Architecture

The project decouples heavy raster computation from web visualization to ensure sub-second dashboard performance:

1. **ETL Pipeline (`src/`)**:
   - `data_access.py`: Programmatically retrieves WorldPop GeoTIFFs (1km constrained) and GADM Level 2 county boundaries with disk caching.
   - `aggregation.py`: Verifies EPSG:4326 CRS alignment, calculates zonal population sums per county, and computes key demographic indicators (Dependency Ratios, Sex Ratios).
   - `validation.py`: Audits cohort completeness, checks for data anomalies, and generates diagnostic plots (`outputs/figures/`).
2. **Interactive UI (`dashboard/`)**:
   - Built with Streamlit and Plotly MapLibre.
   - Visualizes demographic pyramids, choropleth risk surfaces, and comparative bar charts.
   - Includes public health policy translations for resource allocation.

## Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/brianngumbau/ahadi_worldpop.git](https://github.com/brianngumbau/ahadi_worldpop.git)
cd ahadi_worldpop

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install pinned dependencies
pip install -r requirements.txt


Running the Project
# Execute the full pipeline (downloads data & computes county aggregates)
python src/pipeline.py

# Run validation checks and generate static figures
python src/validation.py

# Run automated tests
pytest tests/

# Launch the interactive dashboard
streamlit run dashboard/app.py
