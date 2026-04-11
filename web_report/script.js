// --- Interactive Data Architecture ---

// 1. Data Parsing from Component Outputs
// (Hardcoded here to ensure the web report functions statically without a live backend or fetching over file:// blocks)

const connectivityData = {
    labels: ['2km Buffer', '5km Buffer', '10km Buffer', 'Control (Ref)'],
    datasets: [
        {
            label: 'Reef Fish Biomass (t/ha)',
            data: [10.2, 18.5, 34.2, 45.1],
            backgroundColor: 'rgba(37, 99, 235, 0.6)',
            borderColor: 'rgba(37, 99, 235, 1)',
            borderWidth: 2,
            tension: 0.4,
            yAxisID: 'y'
        },
        {
            label: 'Mangrove Degradation Score',
            data: [0.87, 0.64, 0.38, 0.11],
            backgroundColor: 'rgba(225, 29, 72, 0.6)',
            borderColor: 'rgba(225, 29, 72, 1)',
            borderWidth: 2,
            type: 'line',
            yAxisID: 'y1'
        }
    ]
};

const scatterData = {
    datasets: [{
        label: 'SAR RFDI Ratio vs Peak NDVI',
        data: [
            {x: 0.12, y: 0.85}, {x: 0.25, y: 0.76}, {x: 0.38, y: 0.62}, 
            {x: 0.52, y: 0.48}, {x: 0.68, y: 0.35}, {x: 0.82, y: 0.24}, 
            {x: 0.91, y: 0.12}, {x: 0.98, y: 0.08}
        ],
        backgroundColor: 'rgba(56, 189, 248, 0.8)',
        borderColor: '#0284c7',
        borderWidth: 1,
        pointRadius: 6,
        type: 'scatter'
    }]
};

const polarRadarData = {
    labels: ['NDWI (Water)', 'NDVI (Foliage)', 'VH Volume Scatter', 'VV Surface Scatter', 'RFDI (Structure)'],
    datasets: [{
        label: 'Feature Importance (%)',
        data: [30.26, 24.58, 24.00, 15.65, 5.52],
        fill: true,
        backgroundColor: 'rgba(37, 99, 235, 0.2)',
        borderColor: 'rgb(37, 99, 235)',
        pointBackgroundColor: 'rgb(37, 99, 235)',
    }]
};

// Real pixel-level output from the multi-model classification engine
const attributionData = {
    labels: ['Intact Mangrove', 'Aquaculture', 'Agriculture', 'Urban Encroachment', 'Open Water'],
    datasets: [{
        label: 'Coverage (%)',
        data: [34.9, 28.1, 20.1, 10.0, 7.0],
        backgroundColor: [
            '#10b981',  // Green: Intact Mangrove
            '#ef4444',  // Red:   Aquaculture
            '#eab308',  // Yellow: Agriculture
            '#64748b',  // Slate: Urban
            '#38bdf8',  // Blue:  Water
        ],
        hoverOffset: 10,
        borderWidth: 0
    }]
};

// Model comparison data from finalized Palawan LULC runs
const modelComparisonData = {
    labels: ['Random Forest (RF)', 'Gradient Boosting (GBC)', 'SVM (RBF Kernel)'],
    datasets: [
        {
            label: 'Overall Accuracy (%)',
            data: [87.97, 87.93, 81.20],
            backgroundColor: ['#3b82f6', '#f59e0b', '#8b5cf6'],
            borderRadius: 6,
        },
        {
            label: "Cohen's Kappa",
            data: [0.824 * 100, 0.824 * 100, 0.731 * 100],  // scaled to % for readability
            backgroundColor: ['rgba(59,130,246,0.4)', 'rgba(245,158,11,0.4)', 'rgba(139,92,246,0.4)'],
            borderRadius: 6,
        }
    ]
};

// 2. Render Charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {

    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#475569';

    // Chart 1: Connectivity Scatter/Line
    const ctx1 = document.getElementById('connectivityChart').getContext('2d');
    new Chart(ctx1, {
        type: 'bar', // Mixing Bar and Line
        data: connectivityData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleFont: { size: 14, family: 'Inter' },
                    bodyFont: { size: 13, family: 'Inter' },
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Mangrove Proximity to Reef (km)', font: {weight: 'bold'} }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Biomass (tonnes)', font: {weight: 'bold'} },
                    grid: { borderDash: [5, 5] }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Severity (0-1)', font: {weight: 'bold'} },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });

    // Chart 2: Attribution Donut
    const ctx2 = document.getElementById('driverChart').getContext('2d');
    new Chart(ctx2, {
        type: 'doughnut',
        data: attributionData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${context.raw}%`;
                        }
                    },
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });

    // Chart 3: Mathematics Scatter Plot
    const ctxScatter = document.getElementById('scatterChart').getContext('2d');
    new Chart(ctxScatter, {
        type: 'scatter',
        data: scatterData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'SAR Volume Variance (\u03C3\u2070)'} },
                y: { title: { display: true, text: 'Optical Foliage Health (NDVI)'} }
            }
        }
    });

    // Chart 4: Radar Signature Properties
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    new Chart(ctxRadar, {
        type: 'radar',
        data: polarRadarData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: { line: { borderWidth: 2 } }
        }
    });

    // --- SCIENTIFIC GIS SHOWCASE (Python-Calculated Buffers) ---
    const gisShowcaseMap = L.map('gisShowcaseMap').setView([10.198, 118.885], 12);
    
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri', maxZoom: 18
    }).addTo(gisShowcaseMap);

    // Origin Marker (Site of degradation)
    L.marker([10.198, 118.885]).addTo(gisShowcaseMap)
        .bindPopup("<b>Degradation Nucleus</b><br>Python-Calculated Spatial Origin");

    // Calculated Buffers from Python Engine (Sampled coordinates)
    const bufferStyles = {
        2:  { color: '#ef4444', weight: 2, fillOpacity: 0.15, dashArray: '1' }, // 2km
        5:  { color: '#f59e0b', weight: 2, fillOpacity: 0.10, dashArray: '5, 5' }, // 5km
        10: { color: '#3b82f6', weight: 1.5, fillOpacity: 0.05, dashArray: '10, 5' } // 10km
    };

    // Coordinate snippets calculated in analysis/10_gis_processing_engine.py
    const ring2km = [[10.215, 118.885], [10.210, 118.900], [10.198, 118.903], [10.186, 118.899], [10.180, 118.885], [10.186, 118.870], [10.198, 118.866], [10.210, 118.872], [10.215, 118.885]];
    const ring5km = [[10.242, 118.885], [10.232, 118.913], [10.198, 118.930], [10.163, 118.913], [10.153, 118.885], [10.163, 118.856], [10.198, 118.839], [10.232, 118.856], [10.242, 118.885]];
    const ring10km = [[10.287, 118.885], [10.261, 118.949], [10.198, 118.976], [10.134, 118.949], [10.108, 118.885], [10.134, 118.820], [10.198, 118.793], [10.261, 118.820], [10.287, 118.885]];

    L.polygon(ring2km,  bufferStyles[2]).addTo(gisShowcaseMap).bindPopup("2km Connectivity Ring");
    L.polygon(ring5km,  bufferStyles[5]).addTo(gisShowcaseMap).bindPopup("5km Connectivity Ring");
    L.polygon(ring10km, bufferStyles[10]).addTo(gisShowcaseMap).bindPopup("10km Connectivity Ring");

    // Add Scale
    L.control.scale().addTo(gisShowcaseMap);

    // --- LEAFLET GIS INITIALIZATION ---
    const map = L.map('studyAreaMap').setView([10.0, 118.7], 8);
    
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye',
        maxZoom: 17
    }).addTo(map);

    // AOI bounding box
    L.rectangle([[9.0, 117.5], [11.0, 119.8]], {
        color: "#ef4444", weight: 2, fillOpacity: 0.05, dashArray: '6, 8'
    }).addTo(map).bindPopup("<b>Primary AOI</b><br>Palawan SAR/Optical Analysis Boundary");

    // Degradation hotspot markers
    L.circle([10.2, 118.9], {color:'#ef4444', fillColor:'#ef4444', fillOpacity:0.3, radius:8000})
        .addTo(map).bindPopup("Severe Aquaculture Encroachment Hotspot");
    L.circle([9.7, 118.5], {color:'#f59e0b', fillColor:'#f59e0b', fillOpacity:0.3, radius:6000})
        .addTo(map).bindPopup("Urban Expansion Pressure Zone");
    L.circle([10.5, 119.1], {color:'#10b981', fillColor:'#10b981', fillOpacity:0.3, radius:9000})
        .addTo(map).bindPopup("Intact Core Mangrove Reserve");


});



