# Unified Coastal-Forest Interface Remote Sensing Project

This repository hosts a 7-week Python-based pipeline mapping mangrove degradation severity using SAR backscatter (Sentinel-1), connecting degraded zones to reef nursery proximity, and attributing degradation drivers (LULC classification).

## Focus Area
**Palawan Coast, Philippines**

## Core Stack
- **Data Fetch:** `asf_search` (Sentinel-1 ASF Vertex), `pystac_client` + `stackstac` (Sentinel-2 Planetary Computer).
- **Processing:** `pyroSAR`, `rasterio`, `geopandas`.
- **Machine Learning:** `scikit-learn` (Random Forest Classifier).

## Architecture

1. **`data_pipeline/`**: Scripts fetching optical, SAR, and baseline data explicitly via pure Python APIs.
2. **`analysis/`**:
   - `04_component_a_degradation.py`: Maps mangrove degradation severity using SAR backscatter.
   - `05_component_b_connectivity.py`: Models coral-mangrove buffering limits (proximity indices).
   - `06_component_c_attribution.py`: Identifies degradation drivers via multi-temporal LULC overlays.
3. **`outputs/`**: Research-ready notebooks and draft text anchoring outcomes.

## Key Papers (Gap Analysis)
- **Goldberg et al. (2020)**: Extent loss (binary) vs Degradation.
- **Zhao & Qin (2020)**: SAR backscatter as structural proxy.
- **Friess et al. (2022)**: Drivers of degradation and blue carbon impacts.
- **Phinn et al. (2024)**: Coral reef structural distributions.

## Quickstart

```bash
pip install -r requirements.txt
python data_pipeline/01_fetch_s1_asf.py
...
```
