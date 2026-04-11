# Unified Coastal-Forest Interface Research Project (Palawan, Philippines)

This repository hosts a data-driven Python pipeline for quantifying mangrove structural degradation and its ecological connectivity to adjacent coral reef systems. 

**Research Goal:** To transition from binary "loss" detection toward high-precision structural degradation analysis using fused multi-sensor data.

## 🚀 Key Achievements (Verified March 2024)
- **ML Performance:** Achieved **87.97% Overall Accuracy** (κ = 0.824) using a multi-sensor 6-band Random Forest classifier.
- **Python GIS Engine:** Custom geometric multi-ring buffering (2km, 5km, 10km) computed natively in Python to model reef connectivity.
- **Feature Importance:** Isolated **VH SAR Backscatter** and **NDWI** as the critical signatures for sub-canopy structural trauma attribution.

## 🍱 Portfolio Showcase
High-resolution research assets are ready in `outputs/portfolio/` for academic review:
- `01_project_identity_hero.png`: Technical project branding.
- `02_gis_connectivity_buffers.png`: Python-calculated spatial rings.
- `03_accuracy_assessment_table.png`: Verified multi-model performance.

## 🛠️ Architecture
1. **`data_pipeline/`**: Automated fetching via ASF Search (Sentinel-1) and Planetary Computer (Sentinel-2).
2. **`analysis/`**:
   - `06_component_c_attribution.py`: 6-band driver classification (Agri, Aqua, Urban).
   - `10_gis_processing_engine.py`: Geometric proximity modeling and buffer calculation.
   - `99_verify_lulc_results.py`: Lean multi-model verification sweep.
3. **`web_report/`**: A professional, interactive HTML dashboard showcasing the final report findings.

## 📈 Scientific Context
This baseline bridges the gap between binary deforestation (Goldberg et al., 2020) and undetected sub-canopy structural collapse, utilizing the **Radar Forest Degradation Index (RFDI)** standard.

## 🚀 Quickstart
1. Install dependencies: `pip install -r requirements.txt`
2. Run the 3-model verification: `python analysis/99_verify_lulc_results.py`
3. View the Project Report: `start web_report/index.html`
