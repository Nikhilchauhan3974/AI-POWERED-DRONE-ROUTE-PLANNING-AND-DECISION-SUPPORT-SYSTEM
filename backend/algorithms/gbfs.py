import heapq
import math
from typing import List, Tuple


def run_gbfs(
    grid,
    start: Tuple[int, int],
    end: Tuple[int, int],
    mode: str = "Safe",
    wind_speed: float = 0.0,
    wind_direction: float = 0.0,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Greedy Best-First Search on the GridEnvironment.

    GBFS always expands the node that looks closest to the goal based solely on
    the heuristic h(n) — the straight-line Euclidean distance to the target.
    It ignores actual path cost (unlike A* which combines g+h).
    This makes it very fast but NOT guaranteed to find the shortest path.

    Obstacles: No-Fly Zone cells are never entered.
    The mode/wind params are accepted for API uniformity but do not change GBFS
    priority selection (which is purely heuristic-driven by design).

    Returns:
        path   : List of (x, y) grid cells (greedily shortest-looking route)
        visited: Cells expanded in heuristic priority order (targeted fan)
    """
    if start == end:
        return [start], [start]

    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    pq: list = []
    counter = 0
    heapq.heappush(pq, (heuristic(start, end), counter, start))

    parent = {start: None}
    visited: List[Tuple[int, int]] = []
    visited_set: set = set()
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
        for nx, ny, _ in grid.get_neighbors(cx, cy):
            neighbor = (nx, ny)
            if neighbor not in visited_set and neighbor not in parent:
                parent[neighbor] = curr
                counter += 1
                heapq.heappush(pq, (heuristic(neighbor, end), counter, neighbor))

    path: List[Tuple[int, int]] = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return path, visited
