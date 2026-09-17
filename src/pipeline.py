"""
ETL Pipeline: Raster processing to tabular data.
Reads GeoTIFFs and GeoJSON boundaries, computes zonal statistics, and exports a CSV.
"""
import os
import glob
import pandas as pd
import geopandas as gpd
from rasterstats import zonal_stats

def process_population_data():
    print("Step 1: Loading Administrative Boundaries...")
    # Tomorrow: Load the GeoJSON here
    # gdf_ken = gpd.read_file("../data/gadm41_KEN_2.json")
    
    print("Step 2: Locating GeoTIFFs...")
    # Tomorrow: Use glob to find all the downloaded TIFs
    # tif_files = glob.glob("../data/**/*.tif", recursive=True)
    
    print("Step 3: Running Zonal Statistics...")
    # Tomorrow: Loop through TIFs, extract age/sex from filename, run zonal_stats, and append to a list
    
    print("Step 4: Exporting clean tabular data...")
    # Tomorrow: pd.DataFrame(results).to_csv("../data/processed_population.csv", index=False)

if __name__ == "__main__":
    process_population_data()