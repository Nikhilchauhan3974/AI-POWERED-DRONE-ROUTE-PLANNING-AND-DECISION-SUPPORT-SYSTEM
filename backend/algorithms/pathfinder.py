import math
from typing import List, Tuple, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the distance in meters between two lat/lon coordinates."""
    R = 6371000.0  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class GridEnvironment:
    def __init__(self, bounds: Dict[str, float], cols: int = 40, rows: int = 40):
        self.min_lat = bounds["min_lat"]
        self.min_lon = bounds["min_lon"]
        self.max_lat = bounds["max_lat"]
        self.max_lon = bounds["max_lon"]
        
        self.cols = cols
        self.rows = rows
        
        # Initialize grids: weight = 1.0 (free space), risk = 0.0
        self.grid_costs = [[1.0 for _ in range(cols)] for _ in range(rows)]
        self.grid_risks = [[0.0 for _ in range(cols)] for _ in range(rows)]
        
        # Keep track of which obstacle types occupy which cells (for rich visual feedback)
        self.grid_obstacles = [[None for _ in range(cols)] for _ in range(rows)]

    def latlon_to_grid(self, lat: float, lon: float) -> Tuple[int, int]:
        """Maps coordinate lat/lon to grid indices (x, y) where x is col, y is row."""
        # Calculate proportional position
        x = int(((lon - self.min_lon) / (self.max_lon - self.min_lon)) * self.cols)
        # Flip Y coordinates so standard grid 0,0 is at min_lat, min_lon (bottom-left)
        y = int(((lat - self.min_lat) / (self.max_lat - self.min_lat)) * self.rows)
        
        # Clamp to grid boundaries
        x = max(0, min(self.cols - 1, x))
        y = max(0, min(self.rows - 1, y))
        return x, y

    def grid_to_latlon(self, x: int, y: int) -> Tuple[float, float]:
        """Maps grid cell (x, y) back to the center GPS coordinate."""
        # Find cell centers
        lon = self.min_lon + ((x + 0.5) / self.cols) * (self.max_lon - self.min_lon)
        lat = self.min_lat + ((y + 0.5) / self.rows) * (self.max_lat - self.min_lat)
        return lat, lon

    def apply_obstacles(self, obstacles: List[Dict[str, Any]]):
        """Calculates distance from cell centers and flags grid costs/risks accordingly."""
        for obs in obstacles:
            obs_lat = obs["lat"]
            obs_lon = obs["lon"]
            obs_radius = obs["radius"]
            obs_cost = obs["cost"]
            obs_risk = obs["risk_level"]
            obs_type = obs["type"]

            # Loop through all grid cells and apply obstacle if it falls within the radius
            for y in range(self.rows):
                for x in range(self.cols):
                    cell_lat, cell_lon = self.grid_to_latlon(x, y)
                    dist = haversine_distance(obs_lat, obs_lon, cell_lat, cell_lon)
                    
                    # If within radius (add a tiny buffer for grid discretization)
                    if dist <= obs_radius + 10:
                        # For No-Fly Zones, the cost is infinity
                        if obs_type.lower() == "no-fly zones" or obs_cost >= 999:
                            self.grid_costs[y][x] = float('inf')
                            self.grid_risks[y][x] = 1.0
                            self.grid_obstacles[y][x] = obs_type
                        else:
                            # Apply maximum obstacle cost and risk
                            if obs_cost > self.grid_costs[y][x]:
                                self.grid_costs[y][x] = obs_cost
                            if obs_risk > self.grid_risks[y][x]:
                                self.grid_risks[y][x] = obs_risk
                            self.grid_obstacles[y][x] = obs_type

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int, float]]:
        """Returns valid neighbors of cell (x, y) as list of (nx, ny, move_cost)."""
        neighbors = []
        # 8-direction movements: (dx, dy, step_weight)
        directions = [
            (0, 1, 1.0),    # North
            (1, 0, 1.0),    # East
            (0, -1, 1.0),   # South
            (-1, 0, 1.0),   # West
            (1, 1, 1.414),  # North-East
            (1, -1, 1.414), # South-East
            (-1, -1, 1.414),# South-West
            (-1, 1, 1.414)  # North-West
        ]
        
        for dx, dy, weight in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                # If target cell cost is infinity (No-Fly Zone), it is impassable
                target_cost = self.grid_costs[ny][nx]
                if target_cost == float('inf'):
                    continue
                
                # Combine travel distance weight with the cost multiplier of the destination cell
                move_cost = weight * target_cost
                neighbors.append((nx, ny, move_cost))
                
        return neighbors

    def calculate_path_distance(self, grid_path: List[Tuple[int, int]]) -> float:
        """Returns total length in meters along a given grid path."""
        if len(grid_path) < 2:
            return 0.0
        
        total_dist = 0.0
        for i in range(len(grid_path) - 1):
            x1, y1 = grid_path[i]
            x2, y2 = grid_path[i+1]
            lat1, lon1 = self.grid_to_latlon(x1, y1)
            lat2, lon2 = self.grid_to_latlon(x2, y2)
            total_dist += haversine_distance(lat1, lon1, lat2, lon2)
            
        return total_dist
