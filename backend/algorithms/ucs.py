import heapq
import math
from typing import List, Tuple

def run_ucs(
    grid,
    start: Tuple[int, int],
    end: Tuple[int, int],
    mode: str = "Safe",
    wind_speed: float = 0.0,
    wind_direction: float = 0.0,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Uniform Cost Search (Dijkstra's algorithm) on the GridEnvironment.

    Unlike A*, UCS uses no heuristic – it expands the frontier strictly by
    cumulative path cost g(n).  This guarantees the minimum-cost path.

    Mode modifiers (same semantics as A*):
      - "Fast"  : minimise distance, largely ignore risk
      - "Safe"  : heavily penalise risk zones
      - "Eco"   : favour tailwind directions, penalise headwinds

    Returns:
        path   : ordered list of (x, y) grid cells from start → end
        visited: cells expanded in discovery order (for visualisation)
    """
    if start == end:
        return [start], [start]

    # Pre-compute wind vector once
    wind_rad = math.radians(wind_direction)
    wx = math.sin(wind_rad)          # East component
    wy = math.cos(wind_rad)          # North component
    wind_intensity = min(wind_speed / 60.0, 1.0)

    # Priority queue: (cost, tie-break counter, node)
    pq: list = []
    counter = 0
    heapq.heappush(pq, (0.0, counter, start))

    parent = {start: None}
    g_cost = {start: 0.0}
    visited: List[Tuple[int, int]] = []
    visited_set: set = set()
    found = False

    while pq:
        curr_cost, _, curr = heapq.heappop(pq)

        if curr in visited_set:
            continue

        visited_set.add(curr)
        visited.append(curr)

        if curr == end:
            found = True
            break

        cx, cy = curr

        for nx, ny, base_step_cost in grid.get_neighbors(cx, cy):
            neighbor = (nx, ny)
            if neighbor in visited_set:
                continue

            cell_cost = grid.grid_costs[ny][nx]
            cell_risk = grid.grid_risks[ny][nx]
            step_dist = math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)

            # --- Mode-specific edge cost ---
            if mode.lower() == "fast":
                # Minimise distance; lightly penalise elevated-cost cells
                edge_cost = step_dist * (1.0 + (cell_cost - 1.0) * 0.1)

            elif mode.lower() == "safe":
                # Heavily penalise risky cells so the path bends widely around them
                edge_cost = step_dist * cell_cost + (cell_risk * 80.0 * step_dist)

            elif mode.lower() == "eco":
                # Reduce cost when travelling with the wind, increase against it
                dx, dy = nx - cx, ny - cy
                length = math.sqrt(dx * dx + dy * dy) or 1.0
                tx, ty = dx / length, dy / length
                wind_dot = tx * wx + ty * wy
                wind_multiplier = 1.0 - (0.5 * wind_dot * wind_intensity)
                wind_multiplier = max(0.7, min(1.7, wind_multiplier))
                edge_cost = step_dist * cell_cost * wind_multiplier

            else:
                # Default: pure uniform step cost (no mode weighting)
                edge_cost = base_step_cost

            tentative_g = curr_cost + edge_cost

            if neighbor not in g_cost or tentative_g < g_cost[neighbor]:
                g_cost[neighbor] = tentative_g
                counter += 1
                parent[neighbor] = curr
                heapq.heappush(pq, (tentative_g, counter, neighbor))

    # Reconstruct path from parent map
    path: List[Tuple[int, int]] = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return path, visited
