import json
import math
import os

def calculate_gis_buffers():
    print("[*] Starting Python GIS Buffer Calculation Engine")
    
    # 1. Base Origin (Palawan Core Degradation Scene Center)
    origin_lat = 10.198
    origin_lon = 118.885
    
    # 2. Distance Multipliers (Degrees of Lat/Lon are approx 111km)
    km_to_deg = 1 / 111.32
    
    # Rings to calculate (GIS Task)
    rings = [2, 5, 10] # km
    
    spatial_results = {
        "metadata": {
            "origin": [origin_lat, origin_lon],
            "projection": "EPSG:4326",
            "task": "Multi-Ring Buffer Analysis"
        },
        "geometries": []
    }
    
    # 3. Perform the Buffer Task (Generating geometric rings)
    # This simulates a 'ST_Buffer' or 'geopandas.buffer' operation
    num_segments = 64 # High resolution for smooth curves
    
    for radius_km in rings:
        print(f"    - Calculating {radius_km}km Buffer Geometry...")
        radius_deg = radius_km * km_to_deg
        
        coordinates = []
        for i in range(num_segments + 1):
            angle = (i / num_segments) * 2 * math.pi
            lat_offset = radius_deg * math.cos(angle)
            lon_offset = (radius_deg * math.sin(angle)) / math.cos(math.radians(origin_lat))
            
            coordinates.append([origin_lat + lat_offset, origin_lon + lon_offset])
            
        spatial_results["geometries"].append({
            "type": "BufferRing",
            "radius_km": radius_km,
            "coordinates": coordinates,
            "impact_level": 1.0 - (radius_km / 12.0) # Relative degradation impact
        })

    # 4. Save the calculated GIS Task Output
    output_path = "outputs/spatial_analysis_results.json"
    with open(output_path, "w") as f:
        json.dump(spatial_results, f, indent=4)
        
    print(f"[+] Python GIS Task Complete: {len(rings)} buffers calculated and saved to {output_path}")

if __name__ == "__main__":
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    calculate_gis_buffers()
