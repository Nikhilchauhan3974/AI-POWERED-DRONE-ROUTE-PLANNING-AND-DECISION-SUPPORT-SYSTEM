from collections import deque
from typing import List, Tuple
import math


def run_bfs(
    grid,
    start: Tuple[int, int],
    end: Tuple[int, int],
    mode: str = "Safe",
    wind_speed: float = 0.0,
    wind_direction: float = 0.0,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Breadth-First Search on the GridEnvironment.

    BFS guarantees the *shortest hop-count* path (fewest grid cells traversed).
    It does NOT optimise for distance or cost — this is its fundamental property.

    Obstacles are still respected: No-Fly Zone cells (cost=inf) are never entered.
    The mode/wind parameters are accepted for API uniformity but are not used to
    re-weight edges (BFS is unweighted by definition).

    Returns:
        path   : List of (x, y) grid cells (shortest hop-count route)
        visited: Cells explored in BFS order (wide fan-out pattern)
    """
    if start == end:
        return [start], [start]

    queue: deque = deque([start])
    parent = {start: None}
    visited: List[Tuple[int, int]] = []
    visited_set = {start}
    found = False

    while queue:
        curr = queue.popleft()
        visited.append(curr)

        if curr == end:
            found = True
            break

        cx, cy = curr
        # BFS expands level by level — all neighbors are equal weight (ignoring cost)
        for nx, ny, _ in grid.get_neighbors(cx, cy):
            neighbor = (nx, ny)
            if neighbor not in visited_set:
                visited_set.add(neighbor)
                parent[neighbor] = curr
                queue.append(neighbor)

    path: List[Tuple[int, int]] = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return path, visited
