from typing import List, Tuple
import math


def run_dfs(
    grid,
    start: Tuple[int, int],
    end: Tuple[int, int],
    mode: str = "Safe",
    wind_speed: float = 0.0,
    wind_direction: float = 0.0,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Depth-First Search on the GridEnvironment.

    DFS aggressively follows a single branch as deep as possible before
    backtracking. It does NOT guarantee the shortest or cheapest path —
    the returned path is simply the first complete path DFS discovers.
    This is its fundamental (and often dramatic) characteristic.

    Obstacles: No-Fly Zone cells (cost=inf) are never entered.
    The mode/wind parameters are accepted for API uniformity but do not
    re-weight edges (DFS is unweighted by definition).

    Returns:
        path   : List of (x, y) grid cells (first path DFS discovers)
        visited: Cells explored in DFS order (deep dive pattern)
    """
    if start == end:
        return [start], [start]

    stack = [start]
    parent = {start: None}
    visited: List[Tuple[int, int]] = []
    visited_set: set = set()
    found = False

    while stack:
        curr = stack.pop()

        if curr in visited_set:
            continue

        visited_set.add(curr)
        visited.append(curr)

        if curr == end:
            found = True
            break

        cx, cy = curr
        # DFS dives deep — push all neighbors but only follow the last one first
        for nx, ny, _ in grid.get_neighbors(cx, cy):
            neighbor = (nx, ny)
            if neighbor not in visited_set:
                # Only set parent if not already discovered to keep consistent backtrack
                if neighbor not in parent:
                    parent[neighbor] = curr
                stack.append(neighbor)

    path: List[Tuple[int, int]] = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return path, visited
