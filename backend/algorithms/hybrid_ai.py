from typing import List, Tuple
from backend.algorithms.ida_star import run_idastar
from backend.algorithms.expectimax import run_expectimax
from backend.algorithms.hmm_tracker import HMMTracker

def run_hybrid_ai(grid, start: Tuple[int, int], end: Tuple[int, int], mode: str = "Safe", wind_speed: float = 0.0, wind_direction: float = 0.0) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Combines HMM Tracking, Expectimax, and IDA* for the ultimate AI agent.
    - HMM tracks stochastic obstacles.
    - Expectimax is used for short-range evasion if an obstacle is near.
    - IDA* is used for global pathfinding when safe.
    """
    tracker = HMMTracker(grid.cols, grid.rows)
    
    # Use standard A* for global pathfinding for maximum speed and completion guarantee
    from backend.algorithms.astar import run_astar
    global_path, visited = run_astar(grid, start, end, mode, wind_speed, wind_direction)
    
    if not global_path:
        return [], visited
        
    final_path = [start]
    curr = start
    
    for step_count in range(800):
        if curr == end:
            break
            
        tracker.time_update()
        
        needs_evasion = False
        next_planned = None
        
        try:
            idx = global_path.index(curr)
            if idx + 1 < len(global_path):
                next_planned = global_path[idx + 1]
                # If a sudden extreme risk appears on the next planned step, evade
                if grid.grid_risks[next_planned[1]][next_planned[0]] > 0.8:
                    needs_evasion = True
            else:
                break
        except ValueError:
            needs_evasion = True
            
        if needs_evasion:
            ev_path, _ = run_expectimax(grid, curr, end, depth=3)
            if len(ev_path) > 1:
                curr = ev_path[1]
                # Recalculate global path from new position
                global_path, _ = run_astar(grid, curr, end, mode, wind_speed, wind_direction)
                if not global_path:
                    break
            else:
                # Expectimax completely blocked, fallback to A*
                global_path, _ = run_astar(grid, curr, end, mode, wind_speed, wind_direction)
                if len(global_path) > 1:
                    curr = global_path[1]
                else:
                    break
        else:
            curr = next_planned
            
        final_path.append(curr)
        
    return final_path, visited
