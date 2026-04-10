import os
import asf_search as asf
from datetime import datetime

# Central Palawan Approximate Bounding Box (WKT)
# Covers Honda Bay to Puerto Princesa
PALAWAN_WKT = "POLYGON((118.7 9.7, 119.0 9.7, 119.0 10.0, 118.7 10.0, 118.7 9.7))"

DOWNLOAD_DIR = "../data/raw/sentinel-1"

def fetch_s1_data(start_date: str, end_date: str):
    """
    Query and download Sentinel-1 GRD data for the Palawan AOI.
    We target IW mode and VV+VH polarization.
    """
    print(f"Querying ASF Vertex for S1 from {start_date} to {end_date}...")
    
    results = asf.geo_search(
        platform=[asf.PLATFORM.SENTINEL1],
        intersectsWith=PALAWAN_WKT,
        maxResults=50,
        start=datetime.strptime(start_date, "%Y-%m-%d"),
        end=datetime.strptime(end_date, "%Y-%m-%d"),
        processingLevel=asf.PRODUCT_TYPE.GRD_HD,
        beamMode=asf.BEAMMODE.IW
    )
    
    print(f"Found {len(results)} scenes.")
    
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
    print(f"Data would be downloaded to: {os.path.abspath(DOWNLOAD_DIR)}")
    print("Mocking download for automated pipeline test...")
    # NOTE: To actually download, you'd use:
    # session = asf.ASFSession().auth_with_creds('username', 'password')
    # asf.download_url(url=results[0].properties['url'], path=DOWNLOAD_DIR, session=session)

if __name__ == "__main__":
    fetch_s1_data("2024-01-01", "2024-02-01")
