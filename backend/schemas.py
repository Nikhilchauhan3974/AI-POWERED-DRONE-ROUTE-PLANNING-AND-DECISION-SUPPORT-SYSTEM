from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Coordinate(BaseModel):
    lat: float
    lon: float

class ObstacleCreate(BaseModel):
    type: str
    lat: float
    lon: float
    radius: float  # in meters
    risk_level: float  # 0 to 1
    cost: float  # Traversal cost multiplier

class ObstacleResponse(ObstacleCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WeatherConfig(BaseModel):
    condition: str  # clear, rain, wind, fog, storm
    wind_speed: float  # in km/h
    wind_direction: float  # in degrees (0 = North, 90 = East, etc.)

class RoutePlanRequest(BaseModel):
    source: Coordinate
    destination: Coordinate
    algorithm: str  # BFS, DFS, ASTAR, GBFS
    optimization_mode: str = "Safe"  # Eco, Safe, Fast
    weather: WeatherConfig
    obstacles: List[ObstacleCreate]  # Active user-placed obstacles
    bounds: Optional[Dict[str, float]] = None # Passed from frontend to avoid guessing

class TelemetrySummary(BaseModel):
    speed: float  # km/h
    altitude: float  # meters
    battery_percentage: float  # 0 to 100
    distance: float  # total meters
    nodes_visited: int
    execution_time_ms: float
    cost: float
    risk_score: float

class ObstacleEncountered(BaseModel):
    type: str
    grid_x: int
    grid_y: int
    cost: float
    risk: float

class RoutePlanResponse(BaseModel):
    algorithm: str
    optimization_mode: str = "Safe"
    path: List[Coordinate]  # Final route coordinates
    grid_path: List[List[int]]  # Grid coordinates [x, y]
    visited: List[List[int]]  # Visited grid coordinates [x, y] in order
    telemetry: TelemetrySummary
    battery_profile: List[float]  # Battery at each step
    ai_recommendation: str
    obstacles_encountered: List[Dict[str, Any]] = []  # Obstacles the path passes through
    total_distance: float = 0.0  # Total distance in meters from start to end

class RouteSave(BaseModel):
    name: str
    source_lat: float
    source_lon: float
    dest_lat: float
    dest_lon: float
    algorithm: str
    weather: str
    wind_speed: float
    wind_direction: float
    distance: float
    travel_time: float
    battery_consumed: float
    risk_score: float
    path_coords: List[Coordinate]

class RouteResponse(RouteSave):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    algorithm: str
    avg_execution_time_ms: float
    avg_nodes_visited: float
    avg_path_length: float
    avg_cost: float
    avg_battery_consumed: float
    avg_risk_score: float
    run_count: int

class FleetScheduleRequest(BaseModel):
    drones: List[str]
    stations: List[str]
    time_slots: List[int]

class FleetScheduleResponse(BaseModel):
    schedule: Optional[Dict[str, List[Any]]] # Dict[drone, [station, time_slot]]
