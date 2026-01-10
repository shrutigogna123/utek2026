import numpy as np

# ==========================================
# 1. CONFIGURATION
# ==========================================
GRID_SIZE = 20

# Cell Types (IDs)
ID_HALLWAY = 0
ID_WALL = 1
ID_HUB = 2
ID_MATERNITY = 3
ID_ICU = 4
ID_WAITING = 5
ID_ER = 6
ID_OR = 7

# COORDINATES (Where drones fly to)
# These are centered deep inside the rooms
TARGETS = {
    "Hub": (2, 2),         
    "Maternity": (14, 2),  
    "ICU": (6, 6),         
    "Waiting Room": (2, 16), 
    "ER": (10, 16),        
    "OR": (18, 15)         
}

# ==========================================
# 2. VISUALS (Colors)
# ==========================================
COLOR_MAP = [
    [0.0, "#2b2b2b"],   # 0: Hallway (Dark Grey)
    [0.12, "#2b2b2b"],
    [0.12, "#000000"],  # 1: Wall (Black)
    [0.25, "#000000"],
    [0.25, "#2E8B57"],  # 2: Hub (Green)
    [0.37, "#2E8B57"],
    [0.37, "#4682B4"],  # 3: Maternity (Blue)
    [0.50, "#4682B4"],
    [0.50, "#CD5C5C"],  # 4: ICU (Red)
    [0.62, "#CD5C5C"],
    [0.62, "#DAA520"],  # 5: Waiting (Goldenrod)
    [0.75, "#DAA520"],
    [0.75, "#FF4500"],  # 6: ER (OrangeRed)
    [0.87, "#FF4500"],
    [0.87, "#9370DB"],  # 7: OR (Purple)
    [1.0, "#9370DB"],
]

# Labels
LABELS = [
    {"x": 1, "y": 1, "txt": "HUB"},
    {"x": 1, "y": 14, "txt": "MATERNITY"},
    {"x": 6, "y": 6, "txt": "ICU"},
    {"x": 15, "y": 2, "txt": "WAITING"},
    {"x": 15, "y": 10, "txt": "ER"},
    {"x": 15, "y": 18, "txt": "OR"},
]

# ==========================================
# 3. MAP GENERATION
# ==========================================
def create_floor_plan():
    grid = np.ones((GRID_SIZE, GRID_SIZE), dtype=int) * ID_WALL

    # 1. Carve Hallways (Value 0)
    grid[:, 4:5] = ID_HALLWAY
    grid[:, 8:9] = ID_HALLWAY
    grid[:, 12:13] = ID_HALLWAY
    
    grid[4:5, :] = ID_HALLWAY
    grid[8:9, :] = ID_HALLWAY
    grid[12:13, :] = ID_HALLWAY
    grid[16:17, :] = ID_HALLWAY

    # 2. Place Rooms (Clean Rectangles/Squares)
    # Note: These fit exactly between the hallway lines
    
    # Hub (Top Left)
    grid[0:4, 0:4] = ID_HUB
    
    # Maternity (Bottom Left)
    grid[13:16, 0:8] = ID_MATERNITY
    
    # ICU (Center Left - PERFECT SQUARE NOW)
    # Fits exactly between vertical halls 4&8 and horizontal halls 4&8
    grid[5:8, 5:8] = ID_ICU
    
    # Waiting Room (Top Right)
    grid[0:4, 13:20] = ID_WAITING
    
    # ER (Middle Right)
    grid[9:12, 13:20] = ID_ER
    
    # OR (Bottom Right)
    grid[17:20, 13:17] = ID_OR

    # 3. Connection Fixes
    # We only need to ensure 'doors' exist where a room might be fully walled off.
    # But since our rooms touch the Hallway lines (e.g. ICU 5:8 touches Hall 4:5),
    # the drone can cross directly. 
    # NO EXTRA WINGS ADDED.

    return grid

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def is_walkable(grid, r, c):
    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
        val = grid[r, c]
        return val != ID_WALL
    return False