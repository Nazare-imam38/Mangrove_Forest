import numpy as np
import matplotlib.pyplot as plt
import os

def create_gis_showcase():
    print("[*] Initializing Python GIS Showcase: Palawan Spatial Engine")
    
    # 1. Setup Spatial Bounds (Palawan Focal Zone)
    grid_size = 300
    x = np.linspace(0, 10, grid_size)
    y = np.linspace(0, 10, grid_size)
    X, Y = np.meshgrid(x, y)

    # 2. Simulate "GIS Buffer Task" (Component B)
    # Origin of degradation at center
    origin = [5, 5]
    dist = np.sqrt((X - origin[0])**2 + (Y - origin[1])**2)
    
    # Define Buffers: 2km, 5km, 10km (normalized)
    buffer_2km = (dist <= 1.5)
    buffer_5km = (dist > 1.5) & (dist <= 3.5)
    buffer_10km = (dist > 3.5) & (dist <= 6.0)

    # 3. Simulate Classification Surface (Component C)
    # 0: Water, 1: Intact, 2: Agri/Aqua (Degradation)
    classification = np.zeros((grid_size, grid_size))
    classification[dist < 1.4] = 2  # High degradation core
    classification[(dist >= 1.4) & (dist < 4.0)] = 1 # Intact belt
    
    # Add some "noise" to simulate real LULC complexity
    noise = np.random.rand(grid_size, grid_size)
    classification[noise > 0.96] = 2 # Sparse encroachment patches

    # 4. Generate the GIS Visualization
    plt.figure(figsize=(10, 8), dpi=120)
    
    # Plot Classification Layer as Base
    cmap_lulc = plt.cm.colors.ListedColormap(['#38bdf8', '#16a34a', '#ef4444'])
    plt.imshow(classification, extent=[0, 10, 0, 10], cmap=cmap_lulc, origin='lower', alpha=0.8)

    # Add Buffer Contours (Traditional GIS visualization style)
    contours = plt.contour(X, Y, dist, levels=[1.5, 3.5, 6.0], colors=['white', '#fde68a', '#fda4af'], linestyles='--')
    plt.clabel(contours, inline=True, fontsize=9, fmt={1.5: '2km Buffer', 3.5: '5km Buffer', 6.0: '10km Buffer'})

    # Styling
    plt.title("Palawan GIS Analysis Output: Degradation Connectivity Rings", fontsize=14, pad=20, fontname='sans-serif', fontweight='bold')
    plt.xlabel("Eastings (Relative Units)", fontsize=10)
    plt.ylabel("Northings (Relative Units)", fontsize=10)
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#16a34a', lw=4, label='Intact Mangrove Core'),
        Line2D([0], [0], color='#ef4444', lw=4, label='Classified Degradation (Aqua/Agri)'),
        Line2D([0], [0], color='white', lw=1, ls='--', label='GIS Buffer Boundaries (Connectivity)')
    ]
    plt.legend(handles=legend_elements, loc='upper right', frameon=True, facecolor='black', labelcolor='white', framealpha=0.7)

    plt.grid(True, which='both', color='white', alpha=0.1)
    
    # Save Output
    output_path = "outputs/palawan_gis_analysis.png"
    plt.savefig(output_path, bbox_inches='tight', facecolor='#f8fafc')
    print(f"[+] Success: GIS task showcased at {output_path}")
    plt.close()

if __name__ == "__main__":
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    create_gis_showcase()
