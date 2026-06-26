import math
from typing import List, Tuple

def run_idastar(grid, start: Tuple[int, int], end: Tuple[int, int], mode: str = "Safe", wind_speed: float = 0.0, wind_direction: float = 0.0) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Runs IDA* Search on the GridEnvironment.
    
    Iterative Deepening A* (IDA*) is a memory-bounded variant of A* that uses DFS 
    with a cost limit (f-bound) that increases iteratively.
    """
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
    wind_rad = math.radians(wind_direction)
    wx = math.sin(wind_rad)
    wy = math.cos(wind_rad)
    wind_intensity = min(wind_speed / 60.0, 1.0)
    
    def get_cost(cx, cy, nx, ny, base_cost, cell_cost, cell_risk):
        step_dist = math.sqrt((nx - cx)**2 + (ny - cy)**2)
        if mode.lower() == "fast":
            return step_dist * (1.0 + (cell_cost - 1.0) * 0.1)
        elif mode.lower() == "safe":
            return step_dist * cell_cost + (cell_risk * 80.0 * step_dist)
        elif mode.lower() == "eco":
            dx = nx - cx
            dy = ny - cy
            length = math.sqrt(dx*dx + dy*dy)
            tx = dx / length
            ty = dy / length
            wind_dot = tx * wx + ty * wy
            wind_multiplier = 1.0 - (0.5 * wind_dot * wind_intensity)
            wind_multiplier = max(0.7, min(1.7, wind_multiplier))
            return step_dist * cell_cost * wind_multiplier
        else:
            return base_cost

    bound = heuristic(start, end)
    path = [start]
    visited = []
    
    def search(path, g, bound):
        nonlocal nodes_expanded
        nodes_expanded += 1
        
        # Hard limit to prevent infinite hangs on large grids
        if nodes_expanded > 50000:
            return float('inf'), False
            
        curr = path[-1]
        visited.append(curr)
        # Weighted IDA* (W=2.0) to drastically speed up search at the cost of strict optimality
        f = g + heuristic(curr, end) * 2.0
        
        if f > bound:
            return f, False
        if curr == end:
            return f, True
            
        min_f = float('inf')
        cx, cy = curr
        
        # Sort neighbors by heuristic to improve performance (optional but good practice)
        neighbors = []
        for nx, ny, base_cost in grid.get_neighbors(cx, cy):
            cell_cost = grid.grid_costs[ny][nx]
            cell_risk = grid.grid_risks[ny][nx]
            cost = get_cost(cx, cy, nx, ny, base_cost, cell_cost, cell_risk)
            neighbors.append(((nx, ny), cost))
            
        # Order neighbors to explore promising paths first
        neighbors.sort(key=lambda n: n[1] + heuristic(n[0], end))
        
        for neighbor, cost in neighbors:
            if neighbor not in path:
                path.append(neighbor)
                t, found = search(path, g + cost, bound)
                if found:
                    return t, True
                if t < min_f:
                    min_f = t
                path.pop()
                
        return min_f, False

    bound = heuristic(start, end) * 2.0
    path = [start]
    visited = []
    nodes_expanded = 0
    
    while True:
        t, found = search(path, 0, bound)
        if found:
            return path, visited
        if t == float('inf') or nodes_expanded > 50000:
            return [], visited # No path found or timed out
        bound = t
