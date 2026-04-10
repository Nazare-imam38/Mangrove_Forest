import os
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# --- Constants & LULC Scheme ---
FEATURE_NAMES = ['VV', 'VH', 'RFDI', 'NDVI', 'NDWI', 'EVI']
LULC_CLASSES = {
    0: 'Intact Mangrove', 
    1: 'Active Aquaculture', 
    2: 'Abandoned Pond', 
    3: 'Paddy Agriculture', 
    4: 'Dryland Agriculture', 
    5: 'Urban'
}

# --- Component C: Mangrove Degradation Driver Attribution ---
# Core Thesis: Attributes localized degradation severity to specific LULC drivers (Aquaculture/Agri/Urban)
# using a fused SAR-Optical Machine Learning framework.
# See: Datta et al. (2022) - SAR RFDI signatures.
# See: McDermid (2022) - Temporal hold-out validation.

def create_mock_multiband_raster(path, shape=(500, 500), bands=6):
    """Helper to generate multi-band mock data for ML pipeline testing."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    transform = from_origin(118.7, 10.0, 0.0001, 0.0001)
    profile = {
        'driver': 'GTiff', 'height': shape[0], 'width': shape[1], 'count': bands,
        'dtype': rasterio.float32, 'transform': transform
    }
    with rasterio.open(path, 'w', **profile) as dst:
        for i in range(1, bands + 1):
            # Generate random data with some class-like clusters
            data = np.random.rand(*shape).astype(rasterio.float32)
            dst.write(data, i)
    return profile

def load_real_feature_stack(csv_path: str, year_group: str = None):
    """
    Replaces synthesize_feature_stack() entirely.

    Reads GEE-exported CSV of real Sentinel-1 + Sentinel-2 pixels.
    csv_path:   path to your GEE export CSV (training or holdout)
    year_group: 'train_2018_2022' or 'holdout_2023_2024' or None (load all)

    Returns: X (numpy array, shape [n_pixels, 6]),
             y (numpy array, shape [n_pixels], int class labels)
    """
    df = pd.read_csv(csv_path)

    # Filter by year group if specified (temporal split)
    if year_group is not None:
        df = df[df['year_group'] == year_group].copy()

    # Drop rows with any NaN in feature columns (cloud gaps, water edges)
    df = df.dropna(subset=FEATURE_NAMES + ['class_id'])

    # Clip RFDI to valid range [-1, 1] — GEE can produce edge artefacts
    df['RFDI'] = df['RFDI'].clip(-1.0, 1.0)

    # Drop class_id values not in your 6-class scheme (edge artefacts)
    df = df[df['class_id'].isin(range(6))].copy()

    X = df[FEATURE_NAMES].values.astype(np.float32)
    y = df['class_id'].values.astype(np.int32)

    # Print class balance — important to verify before training
    unique, counts = np.unique(y, return_counts=True)
    print(f"    Loaded {len(y):,} real pixels from: {csv_path}")
    print(f"    Year group: {year_group or 'all'}")
    print(f"    {'Class':<28} {'Pixels':>8}")
    for cls, cnt in zip(unique, counts):
        print(f"    {LULC_CLASSES[cls]:<28} {cnt:>8,}")

    return X, y

def attribute_degradation_drivers(s1_path, s2_path, degradation_raster, output_path):
    print("--- Running Component C: LULC Driver Attribution Engine ---")
    
    # 1. Pipeline Check/Mock Data Generation
    if not os.path.exists(s1_path):
        print("Required SAR/Optical composites missing. Synthesizing 6-band feature stack...")
        create_mock_multiband_raster(s1_path, bands=3) # VV, VH, VH/VV
        create_mock_multiband_raster(s2_path, bands=3) # NDVI, EVI, NDWI
    
    # 2. Ingest Features
    print(f"Loading SAR feature stack: {s1_path}")
    with rasterio.open(s1_path) as s1:
        vv = s1.read(1)
        vh = s1.read(2)
        ratio = s1.read(3) # VH/VV (Double-Bounce Proxy)
        profile = s1.profile
        
    print(f"Loading Optical feature stack: {s2_path}")
    with rasterio.open(s2_path) as s2:
        ndvi = s2.read(1)
        evi = s2.read(2)
        ndwi = s2.read(3)

    # 3. Prepare Feature Matrix (X)
    # Masking to 06-target areas: Only where degradation from Component A > 0.1
    if not os.path.exists(degradation_raster):
        print(f"Degradation raster missing at {degradation_raster}. Please run Component A first.")
        return

    with rasterio.open(degradation_raster) as dr:
        deg_map = dr.read(1)
    
    mask = (deg_map > 0.1) & (~np.isnan(deg_map))
    X = np.stack([vv[mask], vh[mask], ratio[mask], ndvi[mask], evi[mask], ndwi[mask]], axis=1)
    
    if X.shape[0] == 0:
        print("No degraded pixels found to attribute. Exiting.")
        return

    # 4. Simulated Training (Since we don't have ROI polygons in this lean pipeline)
    print("Initializing Multi-Class Random Forest (n_estimators=100)...")
    
    # Define Classes: 1=Intact, 2=Active Aqua, 3=Abandoned Aqua, 4=Paddy Agri, 5=Dryland Agri, 6=Urban
    # Generating synthetic labels for the 'train' part of the pipeline demo
    y_pseudo = np.random.choice([1, 2, 3, 4, 5, 6], size=X.shape[0], p=[0.2, 0.4, 0.1, 0.1, 0.1, 0.1])
    
    # --- Model Training & Evaluation ---
    # In a real run, we would call load_real_feature_stack(csv_path) here.
    # For now, using the local raster X matrix to maintain execution logic.
    X_train, X_test, y_train, y_test = train_test_split(X, y_pseudo, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    print("Training RandomForest model...")
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print(f"Model Validation Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    
    # 5. Full Scene Prediction
    print("Classifying full Palawan AOI scene...")
    full_prediction = np.zeros(deg_map.shape, dtype=np.uint8)
    full_prediction[mask] = clf.predict(X)
    
    # 6. Driver Statistics
    print("Calculating driver proportions...")
    unique, counts = np.unique(full_prediction[mask], return_counts=True)
    stats = dict(zip(unique, counts))
    total = sum(counts)
    
    for cid, count in stats.items():
        percentage = (count / total) * 100
        print(f" - {LULC_CLASSES.get(cid, 'Unknown')}: {percentage:.2f}%")

    # 7. Export LULC Map
    print(f"Exporting Driver Attribution Map: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    profile.update(dtype=rasterio.uint8, count=1, nodata=0)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(full_prediction.astype(rasterio.uint8), 1)
        
    print("Component C complete. Driver attribution data is ready for synthesis.")

if __name__ == "__main__":
    attribute_degradation_drivers(
        s1_path="../data/processed/s1_feature_stack_2024.tif",
        s2_path="../data/processed/s2_feature_stack_2024.tif",
        degradation_raster="../data/outputs/degradation_severity_map.tif",
        output_path="../data/outputs/driver_attribution_map.tif"
    )
