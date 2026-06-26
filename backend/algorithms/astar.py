import heapq
import math
from typing import List, Tuple

def run_astar(grid, start: Tuple[int, int], end: Tuple[int, int], mode: str = "Safe", wind_speed: float = 0.0, wind_direction: float = 0.0) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Runs A* Search on the GridEnvironment.
    
    Incorporates:
    - Mode: "Safe" (heavy risk penalization), "Eco" (wind vector math), "Fast" (distance priority)
    - Returns (path, visited)
    """
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        # Euclidean distance heuristic
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
    # Wind angle vector conversion
    # 0 deg = North (+y), 90 deg = East (+x), 180 deg = South (-y), 270 deg = West (-x)
    wind_rad = math.radians(wind_direction)
    wx = math.sin(wind_rad)
    wy = math.cos(wind_rad)
    
    # Scale wind impact (max 60 km/h is treated as full effect)
    wind_intensity = min(wind_speed / 60.0, 1.0)
    
    pq = []
    # (f_score, tie_breaker, node)
    counter = 0
    heapq.heappush(pq, (0.0, counter, start))
    
    parent = {start: None}
    g_score = {start: 0.0}
    visited = []
    visited_set = set()
    found = False
    
    while pq:
        _, _, curr = heapq.heappop(pq)
        
        if curr in visited_set:
            continue
            
        visited_set.add(curr)
        visited.append(curr)
        
        if curr == end:
            found = True
            break
            
        cx, cy = curr
        
        for nx, ny, base_cost in grid.get_neighbors(cx, cy):
            neighbor = (nx, ny)
            if neighbor in visited_set:
                continue
                
            cell_cost = grid.grid_costs[ny][nx]
            cell_risk = grid.grid_risks[ny][nx]
            
            # Distance of step (1.0 or 1.414)
            step_dist = math.sqrt((nx - cx)**2 + (ny - cy)**2)
            
            if mode.lower() == "fast":
                # Ignore risk mostly, prioritize distance, avoid only impassables
                cost = step_dist * (1.0 + (cell_cost - 1.0) * 0.1)
            elif mode.lower() == "safe":
                # Heavily penalize risk (multiplier of 80.0 makes paths bend widely around obstacles)
                cost = step_dist * cell_cost + (cell_risk * 80.0 * step_dist)
            elif mode.lower() == "eco":
                # Energy optimization: factor wind vector dot product
                dx = nx - cx
                dy = ny - cy
                length = math.sqrt(dx*dx + dy*dy)
                tx = dx / length
                ty = dy / length
                
                # Projection: tx*wx + ty*wy
                # Positive = tailwind (assisting, cost goes down)
                # Negative = headwind (impeding, cost goes up)
                wind_dot = tx * wx + ty * wy
                
                # Multiplier ranges from 0.7 (full tailwind) to 1.7 (full headwind)
                wind_multiplier = 1.0 - (0.5 * wind_dot * wind_intensity)
                wind_multiplier = max(0.7, min(1.7, wind_multiplier))
                
                cost = step_dist * cell_cost * wind_multiplier
            else:
                cost = base_cost
                
            tentative_g = g_score[curr] + cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, end)
                counter += 1
                parent[neighbor] = curr
                heapq.heappush(pq, (f_score, counter, neighbor))
                
    path = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()
        
    return path, visited
