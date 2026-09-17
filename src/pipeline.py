"""
Master ETL Pipeline Controller.
Executes data extraction, validation, and aggregation sequentially.
"""
import logging
from data_access import fetch_gadm_boundaries, fetch_worldpop_data
from aggregation import aggregate_population_data

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_pipeline():
    logging.info("--- STARTING AHADI DATA PIPELINE ---")
    
    logging.info("Step 1: Downloading resources...")
    fetch_gadm_boundaries()
    fetch_worldpop_data()
    
    logging.info("Step 2: Running spatial aggregation and demographics calculations...")
    aggregate_population_data()
    
    logging.info("--- PIPELINE COMPLETE ---")

if __name__ == "__main__":
    run_pipeline()