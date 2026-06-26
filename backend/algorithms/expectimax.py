import math
from typing import List, Tuple, Dict, Any

def run_expectimax(grid, start: Tuple[int, int], end: Tuple[int, int], depth: int = 3) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Runs Expectimax search for a drone evading a stochastic dynamic obstacle (e.g., storm).
    Returns the best immediate path for a given depth.
    (This is a simplified discrete version for the routing engine.)
    """
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        
    # Keep track of recent moves to penalize revisiting and prevent local minima oscillation
    recent_visited = set()
    
    def evaluate(state: Tuple[int, int]) -> float:
        # Lower score is better. Score = distance to goal + risk penalty
        dist = heuristic(state, end)
        risk = grid.grid_risks[state[1]][state[0]] * 100.0
        revisit_penalty = 50.0 if state in recent_visited else 0.0
        return dist + risk + revisit_penalty
        
    def expectimax(state: Tuple[int, int], current_depth: int, is_max_turn: bool) -> float:
        if current_depth == 0 or state == end:
            return evaluate(state)
            
        cx, cy = state
        
        if is_max_turn: # Drone's turn (minimize score)
            best_val = float('inf')
            for nx, ny, _ in grid.get_neighbors(cx, cy):
                val = expectimax((nx, ny), current_depth - 1, False)
                best_val = min(best_val, val)
            return best_val
        else: # Environment's turn (stochastic obstacle movement, maximize score or average)
            # Simplified expected value over possible next states
            total_val = 0.0
            neighbors = grid.get_neighbors(cx, cy)
            if not neighbors: return evaluate(state)
            
            prob = 1.0 / len(neighbors)
            for nx, ny, _ in neighbors:
                val = expectimax((nx, ny), current_depth - 1, True)
                total_val += prob * val
            return total_val

    # Drone makes the first move (MIN agent because we want to minimize distance+risk)
    best_move = start
    best_score = float('inf')
    
    # We will compute a short path by iteratively running expectimax
    path = [start]
    visited = []
    
    curr = start
    for _ in range(500): # Limit max steps to avoid infinite loops
        if curr == end:
            break
            
        visited.append(curr)
        cx, cy = curr
        
        next_move = None
        min_val = float('inf')
        
        for nx, ny, _ in grid.get_neighbors(cx, cy):
            val = expectimax((nx, ny), depth - 1, False)
            if val < min_val:
                min_val = val
                next_move = (nx, ny)
                
        if not next_move:
            break
            
        curr = next_move
        path.append(curr)
        recent_visited.add(curr)
        
        # Keep recent_visited small
        if len(recent_visited) > 10:
            recent_visited.clear()
            
        # Hard break for expectimax infinite loop
        if len(path) > 800:
            break
            
    # If Expectimax fails to reach the end, gracefully append A* fallback path
    if path[-1] != end:
        from backend.algorithms.astar import run_astar
        fallback_path, _ = run_astar(grid, path[-1], end)
        if fallback_path:
            path.extend(fallback_path[1:])
            
    return path, visited
