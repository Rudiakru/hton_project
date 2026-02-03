import numpy as np

def generate_death_heatmap(deaths_coords, grid_size=50, map_max=15000):
    """
    Generiert ein 2D-Histogramm für Todesfälle.
    deaths_coords: Liste von [x, y]
    """
    if not deaths_coords:
        return np.zeros((grid_size, grid_size)).tolist()
    
    x = [c[0] for c in deaths_coords]
    y = [c[1] for c in deaths_coords]
    
    heatmap, xedges, yedges = np.histogram2d(
        x, y, 
        bins=grid_size, 
        range=[[0, map_max], [0, map_max]]
    )
    
    # Normalisierung und Umwandlung in Liste für JSON
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()
        
    return heatmap.T.tolist() # Transponieren für Plotly (y, x)

def generate_victory_heatmap(victory_coords, grid_size=50, map_max=15000):
    """
    Generiert ein 2D-Histogramm für Sieges-Positionen (Objectives/Wins).
    """
    if not victory_coords:
        return np.zeros((grid_size, grid_size)).tolist()
    
    x = [c[0] for c in victory_coords]
    y = [c[1] for c in victory_coords]
    
    heatmap, xedges, yedges = np.histogram2d(
        x, y, 
        bins=grid_size, 
        range=[[0, map_max], [0, map_max]]
    )
    
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()
        
    return heatmap.T.tolist()

def get_hotspots(heatmap, grid_size=50, map_max=15000, threshold=0.7):
    """
    Identifiziert Hotspots in der Heatmap.
    """
    hotspots = []
    heatmap_np = np.array(heatmap)
    
    indices = np.argwhere(heatmap_np >= threshold)
    for idx in indices:
        # Umrechnen von Grid-Indizes in Map-Koordinaten
        # y_idx ist erste Dimension, x_idx die zweite
        y_center = (idx[0] + 0.5) * (map_max / grid_size)
        x_center = (idx[1] + 0.5) * (map_max / grid_size)
        
        # Region benennen (Heuristik)
        region = "Unknown"
        if x_center < 5000 and y_center < 5000:
            region = "Blue Base Area"
        elif x_center > 10000 and y_center > 10000:
            region = "Red Base Area"
        elif 6000 < x_center < 9000 and 6000 < y_center < 9000:
            region = "Mid Lane"
        elif x_center < 4000 and y_center > 11000:
            region = "Top Lane"
        elif x_center > 11000 and y_center < 4000:
            region = "Bot Lane"
        elif 9000 < x_center < 12000 and 9000 < y_center < 12000:
            region = "Baron Pit Area"
        elif 3000 < x_center < 6000 and 3000 < y_center < 6000:
            region = "Dragon Pit Area"
        
        hotspots.append({
            "x": x_center,
            "y": y_center,
            "intensity": float(heatmap_np[idx[0], idx[1]]),
            "region": region
        })
        
    return hotspots
