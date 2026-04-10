import os
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# --- Constants & LULC Scheme ---
# Features present in both training and holdout CSVs
FEATURE_NAMES = ['VV', 'VH', 'RFDI', 'NDVI', 'NDWI']
LULC_CLASSES = {
    0: 'Intact Mangrove', 
    1: 'Active Aquaculture', 
    2: 'Abandoned Pond', 
    3: 'Paddy Agriculture', 
    4: 'Dryland Agriculture', 
    5: 'Urban'
}

# --- Component C: Mangrove Degradation Driver Attribution (Real Data Integration) ---
# Attributes localized degradation severity to specific LULC drivers using SAR-Optical pixels.

def load_samples(csv_path: str):
    """
    Reads ground truth CSV samples exported from GEE.
    """
    if not os.path.exists(csv_path):
        print(f"Error: Sample data missing at {csv_path}")
        return None, None
        
    df = pd.read_csv(csv_path)

    # Drop rows with any NaN in core features or class_id
    df = df.dropna(subset=FEATURE_NAMES + ['class_id'])

    # Clip RFDI to valid range [-1, 1] (GEE artefact handling)
    if 'RFDI' in df.columns:
        df['RFDI'] = df['RFDI'].clip(-1.0, 1.0)

    # Ensure class_ids are strictly within our 0-5 scheme
    df = df[df['class_id'].isin(range(6))].copy()

    X = df[FEATURE_NAMES].values.astype(np.float32)
    y = df['class_id'].values.astype(np.int32)

    print(f"    Loaded {len(y):,} real pixels from: {os.path.basename(csv_path)}")
    return X, y

def attribute_degradation_drivers(s1_path, s2_path, degradation_raster, training_csv, holdout_csv, output_path):
    print("\n--- Running Component C: LULC Driver Attribution Engine (Palawan) ---")
    
    # 1. Load Data
    print("Loading Ground Truth samples...")
    X_train, y_train = load_samples(training_csv)
    X_val, y_val = load_samples(holdout_csv)
    
    if X_train is None or X_val is None:
        return

    # 2. Train Random Forest Classifier
    print(f"Training Multi-Class Random Forest (Features: {', '.join(FEATURE_NAMES)})...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
    clf.fit(X_train, y_train)
    
    # 3. Temporal Validation
    y_pred_val = clf.predict(X_val)
    acc = accuracy_score(y_val, y_pred_val)
    print(f"✅ Temporal Validation Accuracy (Holdout 2023-24): {acc:.4f}")
    
    # 4. Driver Attribution on Degraded Pixels (Spatial Application)
    if not os.path.exists(degradation_raster):
        print(f"Skipping spatial map: Degradation raster missing at {degradation_raster}")
        return

    print(f"Applying model to degraded zones in: {os.path.basename(degradation_raster)}")
    with rasterio.open(degradation_raster) as dr:
        deg_map = dr.read(1)
        profile = dr.profile
    
    # Load corresponding feature layers for prediction (VV, VH, RFDI, NDVI, NDWI)
    # This logic assumes paths exist; if not, we skip the final map generation layer
    try:
        with rasterio.open(s1_path) as s1:
            vv = s1.read(1)
            vh = s1.read(2)
            # RFDI = (VV-VH)/(VV+VH) if not explicitly stored in band 3
            rfdi = (vv - vh) / (vv + vh + 1e-6) 
            
        with rasterio.open(s2_path) as s2:
            ndvi = s2.read(1)
            ndwi = s2.read(3) # Assumed band order
    except:
        print("Raster feature stacks (S1/S2) missing. Driver stats will be based on holdout dataset proportions.")
        unique, counts = np.unique(y_pred_val, return_counts=True)
        stats = dict(zip(unique, counts))
    else:
        # Spatial Masking: Only attribute where degradation > 0.1
        mask = (deg_map > 0.1) & (~np.isnan(deg_map))
        X_spatial = np.stack([vv[mask], vh[mask], rfdi[mask], ndvi[mask], ndwi[mask]], axis=1)
        
        full_prediction = np.zeros(deg_map.shape, dtype=np.uint8)
        full_prediction[mask] = clf.predict(X_spatial)
        
        # Calculate statistics
        unique, counts = np.unique(full_prediction[mask], return_counts=True)
        stats = dict(zip(unique, counts))

        # Export Map
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        profile.update(dtype=rasterio.uint8, count=1, nodata=0)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(full_prediction.astype(rasterio.uint8), 1)
        print(f"Driver Attribution Map exported to: {output_path}")

    # 5. Print Driver Breakdown
    print("\nDetailed Driver Proportions (Degraded Areas):")
    total = sum(stats.values())
    for cid in range(6):
        count = stats.get(cid, 0)
        percentage = (count / total) * 100 if total > 0 else 0
        print(f" - {LULC_CLASSES[cid]:<22}: {percentage:>6.2f}% ({count:,} pixels)")

    print("\nComponent C complete.")

if __name__ == "__main__":
    attribute_degradation_drivers(
        s1_path="data/processed/s1_sar_2024.tif",
        s2_path="data/processed/s2_ndvi_2024.tif",
        degradation_raster="data/outputs/degradation_severity_map.tif",
        training_csv="outputs/csv/palawan_lulc_training_samples.csv",
        holdout_csv="outputs/csv/palawan_lulc_holdout_samples.csv",
        output_path="data/outputs/palawan_driver_attribution_map.tif"
    )
