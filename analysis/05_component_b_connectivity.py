import os
import csv
import numpy as np
import rasterio
from rasterio.mask import mask
try:
    import geopandas as gpd
    from shapely.geometry import mapping
except ImportError:
    gpd = None

# --- Component B: Coral-Mangrove Connectivity Index (Refined) ---
# Thesis: Quantifies forest degradation within ecological nursery buffers (2km - 10km) around reef units.
# See: Phinn et al. (2024) - Mapping reef structural dependency.

def compute_connectivity_index(degradation_raster, reef_shp, output_stats):
    """
    Overlays degradation severity with reef proximities.
    Extracts mean degradation and degraded area (km2) across 2, 5, and 10km rings.
    """
    print("\n--- Running Component B: Palawan Connectivity Engine ---")
    
    if gpd is None:
        print("Error: geopandas/shapely is missing. Cannot perform spatial buffering.")
        return

    if not os.path.exists(degradation_raster):
        print(f"Error: Required degradation map missing at {degradation_raster}. Run Component A first.")
        # Simulating output for the demo if raster isn't built yet
        return

    if not os.path.exists(reef_shp):
        # Fallback to demo mode if baseline data is missing
        print(f"Warning: Baseline reef shapefile missing at {reef_shp}. Using internal Palawan demo coordinates.")
        reefs = gpd.GeoDataFrame(
            {'id': ['P_REEF_01', 'P_REEF_02', 'P_REEF_03', 'P_REEF_04']}, 
            geometry=gpd.points_from_xy([118.75, 118.82, 118.88, 118.91], [9.85, 9.78, 9.92, 9.95]),
            crs="EPSG:4326"
        ).to_crs("EPSG:32651") # Project to UTM 51N (Palawan) for accurate buffering in meters
    else:
        reefs = gpd.read_file(reef_shp).to_crs("EPSG:32651")

    # Target Proximity Zones
    buffer_dists = [2000, 5000, 10000] # 2km, 5km, 10km
    results = []

    print(f"Analyzing {len(reefs)} reef units across {len(buffer_dists)} connectivity zones...")
    
    with rasterio.open(degradation_raster) as src:
        nodata = src.nodata if src.nodata is not None else 0
        
        for idx, reef in reefs.iterrows():
            entry = {"Reef_ID": reef['id'], "Lon": reef.geometry.centroid.x, "Lat": reef.geometry.centroid.y}
            
            for dist in buffer_dists:
                # Buffer geometry in meters
                buf_geom = reef.geometry.buffer(dist)
                
                # Transform to raster CRS for masking
                buf_geom_trans = gpd.GeoSeries([buf_geom], crs=reefs.crs).to_crs(src.crs).iloc[0]
                
                try:
                    out_image, _ = mask(src, [mapping(buf_geom_trans)], crop=True)
                    data = out_image[0]
                    valid = data[(data != nodata) & (~np.isnan(data))]
                    
                    if valid.size > 0:
                        score = np.mean(valid)
                        # Pixel size in km2 (approximate)
                        area = (valid > 0.1).sum() * (abs(src.res[0] * src.res[1]) / 1e6)
                    else:
                        score, area = 0.0, 0.0
                except (ValueError, IndexError):
                    score, area = 0.0, 0.0
                
                dist_km = dist // 1000
                entry[f"DegScore_{dist_km}km"] = round(float(score), 4)
                entry[f"DegArea_{dist_km}km"] = round(float(area), 4)
            
            results.append(entry)

    # Export Statistics
    os.makedirs(os.path.dirname(output_stats), exist_ok=True)
    if results:
        keys = results[0].keys()
        with open(output_stats, 'w', newline='') as f:
            dw = csv.DictWriter(f, fieldnames=keys)
            dw.writeheader()
            dw.writerows(results)
        print(f"✅ Connectivity Stats exported to: {output_stats}")

if __name__ == "__main__":
    compute_connectivity_index(
        degradation_raster="data/outputs/degradation_severity_map.tif",
        reef_shp="data/baselines/reef_distribution.shp",
        output_stats="data/outputs/connectivity_index.csv"
    )

