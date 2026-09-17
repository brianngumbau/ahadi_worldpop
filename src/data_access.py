"""
Module for programmatically downloading WorldPop raster data and GADM boundaries.
"""
import os
import requests
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def download_file(url, dest_path):
    """Downloads a file if it doesn't already exist."""
    if os.path.exists(dest_path):
        logging.info(f"Cached: {os.path.basename(dest_path)}")
        return dest_path
        
    logging.info(f"Downloading: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return None

def fetch_gadm_boundaries():
    """Downloads and extracts Kenya GADM Level 2 GeoJSON."""
    url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_KEN_2.json.zip"
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    zip_path = os.path.join(raw_dir, "gadm41_KEN_2.json.zip")
    json_path = os.path.join(raw_dir, "gadm41_KEN_2.json")
    
    if not os.path.exists(json_path):
        download_file(url, zip_path)
        if os.path.exists(zip_path):
            logging.info("Extracting GADM boundaries...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(raw_dir)
    return json_path

def fetch_worldpop_data():
    """Constructs URLs and downloads WorldPop GeoTIFFs for Kenya (2021-2025)."""
    # Exact WorldPop R2025A structure based on server index
    base_url = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030/R2025A"
    sexes = ['f', 'm']
    ages = [0, 1] + list(range(5, 85, 5)) # 0, 1, 5, 10... 80
    
    raw_dir = os.path.join("data", "raw", "worldpop")
    os.makedirs(raw_dir, exist_ok=True)
    
    # download 2025 first so i can start testing the dashboard immediately
    for year in [2025, 2024, 2023, 2022, 2021]:
        for sex in sexes:
            for age in ages:
                # WorldPop zero-pads the age (00, 01, 05, 10)
                age_str = f"{age:02d}" 
                
                filename = f"ken_{sex}_{age_str}_{year}_CN_1km_R2025A_UA_v1.tif"
                url = f"{base_url}/{year}/KEN/v1/1km_ua/constrained/{filename}"
                
                dest_path = os.path.join(raw_dir, filename)
                download_file(url, dest_path)

if __name__ == "__main__":
    fetch_gadm_boundaries()
    fetch_worldpop_data()