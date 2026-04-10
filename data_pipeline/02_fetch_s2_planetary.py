import os
from pystac_client import Client

# Planetary Computer STAC endpoint
STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "sentinel-2-l2a"

# Central Palawan Bounding Box [minx, miny, maxx, maxy]
PALAWAN_BBOX = [118.7, 9.7, 119.0, 10.0]

def fetch_s2_data(start_date: str, end_date: str):
    """
    Search Planetary Computer for Sentinel-2 MSI L2A data over Palawan.
    """
    print(f"Connecting to Planetary Computer: {STAC_API_URL}")
    catalog = Client.open(STAC_API_URL)
    
    time_range = f"{start_date}/{end_date}"
    
    print(f"Querying {COLLECTION} for BBOX: {PALAWAN_BBOX} between {time_range}...")
    search = catalog.search(
        collections=[COLLECTION],
        bbox=PALAWAN_BBOX,
        datetime=time_range,
        query={"eo:cloud_cover": {"lt": 5}} # Max 5% cloud cover
    )
    
    items = search.item_collection()
    print(f"Found {len(items)} scenes with <5% cloud cover.")
    
    if len(items) == 0:
        print("No items found.")
        return
        
    # Print standard metadata to verify acquisition
    print("Fetching first scene metadata to demonstrate valid connection...")
    first_item = items[0]
    print(f"Scene ID: {first_item.id}")
    print(f"Cloud Cover: {first_item.properties['eo:cloud_cover']}%")
    print(f"B04 (Red) download link: {first_item.assets['B04'].href}")
    print(f"B08 (NIR) download link: {first_item.assets['B08'].href}")
    print("Script executed successfully. Data ready for Component A.")

if __name__ == "__main__":
    fetch_s2_data("2024-01-01", "2024-02-01")
