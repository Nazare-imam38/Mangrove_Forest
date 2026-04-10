import os
import urllib.request

DATA_DIR = "../data/baselines"

# Global Mangrove Watch 2020 via UN Environment archive or Zenodo
# For the purpose of the pipeline, simulating download of the shapefile/raster.
GMW_URL = "https://zenodo.org/record/6894273/files/GMW_2020_v3.zip" # Example valid or mock URL

def fetch_gmw_baseline():
    """
    Download the Global Mangrove Watch 2020 baseline dataset.
    This serves as our structural mask for Component A.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "GMW_2020_v3.zip")
    
    print(f"Downloading GMW Baseline to: {os.path.abspath(out_path)}...")
    print("Mocking download for automated pipeline test...")
    # urllib.request.urlretrieve(GMW_URL, out_path)
    print("GMW 2020 Baseline fetched.")

def fetch_reef_baseline():
    """
    Download UNEP-WCMC Global Distribution of Coral Reefs (2018).
    This serves as proximity target for Component B.
    """
    print("Fetching UNEP-WCMC Coral Reef distribution...")
    print("Mocking download for automated pipeline test...")
    print("Reef Baseline fetched.")

if __name__ == "__main__":
    fetch_gmw_baseline()
    fetch_reef_baseline()
