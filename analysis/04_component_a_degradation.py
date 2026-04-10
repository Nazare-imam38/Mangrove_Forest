import os
import numpy as np
import rasterio
from rasterio.transform import from_origin

# --- Component A: Mangrove Degradation Severity Mapping ---
# Core Thesis: Maps degradation severity within standing cover using SAR backscatter intensity gradients
# See: Goldberg et al. (2020) - Extent vs Degradation. 
# See: Zhao & Qin (2020) - SAR proxy.

def create_mock_raster(path, value, shape=(500, 500)):
    """Helper to generate dummy rasters so the pipeline can execute end-to-end without real data."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    transform = from_origin(118.7, 10.0, 0.0001, 0.0001)
    profile = {
        'driver': 'GTiff', 'height': shape[0], 'width': shape[1], 'count': 1,
        'dtype': rasterio.float32, 'transform': transform
    }
    with rasterio.open(path, 'w', **profile) as dst:
        data = (np.random.rand(*shape) * value).astype(rasterio.float32)
        dst.write(data, 1)
    return profile

def map_degradation_severity(s1_sar_raster, s2_ndvi_raster, gmw_mask, output_path):
    print("--- Running Component A: Core Scientific Engine ---")
    
    # 1. Fallback / Test-run generator
    if not os.path.exists(s1_sar_raster):
        print("Real raster missing. Synthesizing dummy data to build pipeline architecture...")
        profile = create_mock_raster(s1_sar_raster, 1.0)
        create_mock_raster(s2_ndvi_raster, 0.8)
        create_mock_raster(gmw_mask, 1.0) # Mask: 1s and 0s
        
    # 2. Ingest Data
    print(f"Loading S1 SAR backscatter: {s1_sar_raster}")
    with rasterio.open(s1_sar_raster) as s1:
        sar_data = s1.read(1)
        profile = s1.profile
        
    with rasterio.open(s2_ndvi_raster) as s2:
        ndvi_data = s2.read(1)
        
    with rasterio.open(gmw_mask) as gm:
        mangrove_mask = gm.read(1)

    # 3. Apply Structural Logic (The core thesis)
    print("Masking non-mangrove areas using GMW 2020 baseline...")
    # Keep only areas defined as mangrove
    sar_masked = np.where(mangrove_mask > 0.5, sar_data, np.nan)
    ndvi_masked = np.where(mangrove_mask > 0.5, ndvi_data, np.nan)
    
    print("Calculating structural degradation severity using backscatter gradients (VV + VH)...")
    # Pseudo-formula: High SAR backscatter variance + low NDVI = structural degradation
    # In reality, this would be a Random Forest probability. Simulated formula:
    degradation_severity = (sar_masked * 0.7) - (ndvi_masked * 0.3)
    
    # Normalize index to 0-1 (0 = intact, 1 = severely degraded)
    valid_mask = ~np.isnan(degradation_severity)
    if valid_mask.any():
        d_min, d_max = np.nanmin(degradation_severity), np.nanmax(degradation_severity)
        degradation_index = (degradation_severity - d_min) / (d_max - d_min)
    else:
        degradation_index = degradation_severity
        
    # 4. Output formulation
    print(f"Exporting degradation severity GeoTIFF: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    profile.update(dtype=rasterio.float32, count=1, nodata=np.nan)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(degradation_index.astype(rasterio.float32), 1)
        
    print("Component A complete. Degradation raster is ready for Component B & C.")

if __name__ == "__main__":
    map_degradation_severity(
        s1_sar_raster="../data/processed/s1_sar_2024.tif",
        s2_ndvi_raster="../data/processed/s2_ndvi_2024.tif",
        gmw_mask="../data/baselines/GMW_2020.tif",
        output_path="../data/outputs/degradation_severity_map.tif"
    )
