"""
Module for aggregating raster data to administrative boundaries and calculating demographic indicators.
"""
import os
import glob
import pandas as pd
import geopandas as gpd
from rasterstats import zonal_stats
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def aggregate_population_data():
    gadm_path = os.path.join("data", "raw", "gadm41_KEN_2.json")
    raster_dir = os.path.join("data", "raw", "worldpop")
    output_csv = os.path.join("data", "processed", "kenya_population_by_county.csv")
    
    if not os.path.exists(gadm_path):
        logging.error("GADM boundaries not found. Run data_access.py first.")
        return
        
    logging.info("Loading GADM boundaries...")
    gdf = gpd.read_file(gadm_path)
    
    # Validation: Ensure CRS is EPSG:4326 (Requirement 1.2)
    if gdf.crs.to_string() != "EPSG:4326":
        logging.info(f"Reprojecting boundaries from {gdf.crs} to EPSG:4326")
        gdf = gdf.to_crs(epsg=4326)
        
    # Extract county names
    county_col = 'NAME_1' if 'NAME_1' in gdf.columns else 'NAME_2'
    counties = gdf[county_col].tolist()
    
    tif_files = glob.glob(os.path.join(raster_dir, "*.tif"))
    logging.info(f"Found {len(tif_files)} raster files to process.")
    
    if len(tif_files) == 0:
        logging.error("No GeoTIFFs found. Still downloading?")
        return

    # Dictionary to accumulate totals: data_dict[year][county] = metrics
    data_dict = {}
    
    for tif in tif_files:
        basename = os.path.basename(tif)
        parts = basename.split('_')
        
        # Parse filename (e.g., ken_f_0_2025_1km.tif)
        try:
            sex = parts[1].upper() # 'F' or 'M'
            age = int(parts[2])
            year = int(parts[3])
        except (IndexError, ValueError):
            logging.warning(f"Unrecognized file format, skipping: {basename}")
            continue
            
        if year not in data_dict:
            data_dict[year] = {c: {'M': 0, 'F': 0, 'children': 0, 'working': 0, 'elderly': 0, 'total': 0} for c in counties}
            
        logging.info(f"Processing: {basename}")
        
        # Zonal statistics: Sum the population pixels within each county polygon
        stats = zonal_stats(gdf, tif, stats="sum", nodata=-99999)
        
        for i, county in enumerate(counties):
            pop_sum = stats[i]['sum']
            if pop_sum is None or pop_sum < 0:
                pop_sum = 0 # Handle negative/null values gracefully
                
            data_dict[year][county]['total'] += pop_sum
            data_dict[year][county][sex] += pop_sum
            
            # Age Buckets based on WorldPop naming (0, 1, 5, 10... 80)
            if age in [0, 1]:  # 0-1 and 1-4 make up under 5
                data_dict[year][county]['children'] += pop_sum
            elif 15 <= age <= 64:
                data_dict[year][county]['working'] += pop_sum
            elif age >= 65:
                data_dict[year][county]['elderly'] += pop_sum

    logging.info("Calculating final demographic indicators...")
    final_rows = []
    
    for year, county_data in data_dict.items():
        for county, metrics in county_data.items():
            t = metrics['total']
            c = metrics['children']
            w = metrics['working']
            e = metrics['elderly']
            m = metrics['M']
            f = metrics['F']
            
            # Prevent Division by Zero
            w_safe = w if w > 0 else 1
            f_safe = f if f > 0 else 1
            t_safe = t if t > 0 else 1
            
            row = {
                'county': county,
                'year': year,
                'total_population': round(t, 2),
                'children_under_5': round(c, 2),
                'working_age': round(w, 2),
                'elderly_65plus': round(e, 2),
                'sex_ratio': round((m / f_safe) * 100, 2),
                'dependency_ratio': round(((c + e) / w_safe) * 100, 2),
                'child_dependency_ratio': round((c / w_safe) * 100, 2),
                'elderly_dependency_ratio': round((e / w_safe) * 100, 2),
                'pct_children': round((c / t_safe) * 100, 2),
                'pct_elderly': round((e / t_safe) * 100, 2)
            }
            final_rows.append(row)
            
    df = pd.DataFrame(final_rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    logging.info(f"SUCCESS: Exported clean dataset to {output_csv}")

if __name__ == "__main__":
    aggregate_population_data()