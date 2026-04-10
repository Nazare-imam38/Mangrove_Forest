import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# --- Palawan LULC Verification (Lean Mode) ---
# Direct CSV ingestion utilizing NumPy/Scikit-Learn to bypass GIS dependency issues.

TRAIN_CSV = "outputs/csv/palawan_lulc_training_samples.csv"
HOLDOUT_CSV = "outputs/csv/palawan_lulc_holdout_samples.csv"
FEATURE_NAMES = ['VV', 'VH', 'RFDI', 'NDVI', 'NDWI']
LULC_CLASSES = ['Intact Mangrove', 'Active Aquaculture', 'Abandoned Pond', 'Paddy Agriculture', 'Dryland Agriculture', 'Urban']

from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import cohen_kappa_score

def lean_verify():
    print("\n" + "="*50)
    print(" PALAWAN LULC MULTI-MODEL COMPARISON: VERIFICATION ")
    print("="*50)
    
    if not os.path.exists(TRAIN_CSV):
        print(f"FAIL: Training data not found at {TRAIN_CSV}")
        return

    try:
        train_data = np.genfromtxt(TRAIN_CSV, delimiter=',', skip_header=1, usecols=(0,1,2,3,4,5))
        holdout_raw = np.genfromtxt(HOLDOUT_CSV, delimiter=',', skip_header=1, usecols=(0,1,2,3,4,6))
        train_data = train_data[~np.isnan(train_data).any(axis=1)]
        holdout_raw = holdout_raw[~np.isnan(holdout_raw).any(axis=1)]
    except Exception as e:
        print(f"ERROR: {e}")
        return

    X_train, y_train = train_data[:, :5], train_data[:, 5].astype(int)
    X_val, y_val = holdout_raw[:, :5], holdout_raw[:, 5].astype(int)

    models = {
        "Random Forest (RF)": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "SVM (RBF Kernel)": SVC(kernel='rbf', probability=True, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
    }

    results = {}

    for name, clf in models.items():
        print(f"[*] Training {name}...")
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_val)
        
        acc = accuracy_score(y_val, y_pred)
        kappa = cohen_kappa_score(y_val, y_pred)
        results[name] = (acc, kappa)
        
        print(f"    - Accuracy: {acc:.4f} | Kappa: {kappa:.44f}")

    print("\n" + "="*50)
    print(" FINAL VERIFIED COMPARISON FOR WEB REPORT ")
    print("="*50)
    for name, (acc, kappa) in results.items():
        print(f"{name:<20}: OA={acc*100:.2f}%, K={kappa:.4f}")

    # Feature Importance (RF only)
    rf_clf = models["Random Forest (RF)"]
    importances = rf_clf.feature_importances_
    print("\nRF Feature Importance:")
    for name, imp in zip(FEATURE_NAMES, importances):
        print(f" - {name:<6}: {imp*100:>6.2f}%")

if __name__ == "__main__":
    lean_verify()
