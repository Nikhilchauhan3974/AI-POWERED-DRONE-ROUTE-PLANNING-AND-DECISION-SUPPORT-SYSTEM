import pytest
import math
from backend.algorithms.pathfinder import GridEnvironment
from backend.algorithms.bfs import run_bfs
from backend.algorithms.dfs import run_dfs
from backend.algorithms.astar import run_astar
from backend.algorithms.gbfs import run_gbfs
from backend.weather import TelemetryEngine

@pytest.fixture
def sample_grid():
    # Manhattan Central bounds
    bounds = {"min_lat": 40.760, "min_lon": -73.990, "max_lat": 40.805, "max_lon": -73.950}
    return GridEnvironment(bounds, cols=40, rows=40)

def test_coordinate_mapping(sample_grid):
    # Test mapping of center coordinate
    lat = (sample_grid.min_lat + sample_grid.max_lat) / 2
    lon = (sample_grid.min_lon + sample_grid.max_lon) / 2
    
    x, y = sample_grid.latlon_to_grid(lat, lon)
    assert 0 <= x < 40
    assert 0 <= y < 40
    
    # Test mapping back
    mapped_lat, mapped_lon = sample_grid.grid_to_latlon(x, y)
    assert math.isclose(lat, mapped_lat, abs_tol=0.01)
    assert math.isclose(lon, mapped_lon, abs_tol=0.01)

def test_obstacle_avoidance(sample_grid):
    # Set start and end
    start = (5, 5)
    end = (5, 15)
    
    # Place a massive impassable obstacle blocking the direct line between start and end (x=5, y=10)
    obstacle_lat, obstacle_lon = sample_grid.grid_to_latlon(5, 10)
    obstacles = [{
        "type": "No-Fly Zones",
        "lat": obstacle_lat,
        "lon": obstacle_lon,
        "radius": 400.0, # large radius to cover the route
        "risk_level": 1.0,
        "cost": 999.0 # impassable
    }]
    
    sample_grid.apply_obstacles(obstacles)
    
    # Verify the cell cost is infinity
    ox, oy = sample_grid.latlon_to_grid(obstacle_lat, obstacle_lon)
    assert sample_grid.grid_costs[oy][ox] == float('inf')
    
    # Run A* to verify it bypasses the obstacle
    path, visited = run_astar(sample_grid, start, end, mode="Safe")
    assert len(path) > 0
    
    # Ensure the path never goes through the obstacle coordinate
    for px, py in path:
        assert px != ox or py != oy

def test_all_algorithms(sample_grid):
    start = (2, 2)
    end = (8, 8)
    
    # BFS
    bfs_path, bfs_visited = run_bfs(sample_grid, start, end)
    assert len(bfs_path) >= 2
    assert bfs_path[0] == start
    assert bfs_path[-1] == end
    
    # DFS
    dfs_path, dfs_visited = run_dfs(sample_grid, start, end)
    assert len(dfs_path) >= 2
    assert dfs_path[0] == start
    assert dfs_path[-1] == end
    
    # A*
    astar_path, astar_visited = run_astar(sample_grid, start, end, mode="Safe")
    assert len(astar_path) >= 2
    assert astar_path[0] == start
    assert astar_path[-1] == end
    
    # GBFS
    gbfs_path, gbfs_visited = run_gbfs(sample_grid, start, end)
    assert len(gbfs_path) >= 2
    assert gbfs_path[0] == start
    assert gbfs_path[-1] == end

def test_telemetry_simulation(sample_grid):
    start = (5, 5)
    end = (10, 10)
    astar_path, _ = run_astar(sample_grid, start, end, mode="Safe")
    
    sim = TelemetryEngine.simulate_flight(
        sample_grid,
        astar_path,
        weather_cond="clear",
        wind_speed=15.0,
        wind_direction=45.0
    )
    
    assert sim["distance"] > 0
    assert sim["travel_time"] > 0
    assert 0 <= sim["battery_consumed"] <= 100
    assert len(sim["battery_profile"]) == len(astar_path)
    assert len(sim["altitude_profile"]) == len(astar_path)
    assert len(sim["speed_profile"]) == len(astar_path)
