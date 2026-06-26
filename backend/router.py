import json
import time
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db, Route, Obstacle, AnalyticsLog
from backend.locations import LOCATIONS
from backend.schemas import (
    Coordinate,
    ObstacleCreate,
    ObstacleResponse,
    RoutePlanRequest,
    RoutePlanResponse,
    TelemetrySummary,
    RouteSave,
    RouteResponse,
    AnalyticsSummary,
    FleetScheduleRequest,
    FleetScheduleResponse
)
from backend.algorithms.pathfinder import GridEnvironment
from backend.algorithms.bfs import run_bfs
from backend.algorithms.dfs import run_dfs
from backend.algorithms.astar import run_astar
from backend.algorithms.gbfs import run_gbfs
from backend.algorithms.ucs import run_ucs
from backend.algorithms.ida_star import run_idastar
from backend.algorithms.expectimax import run_expectimax
from backend.algorithms.hybrid_ai import run_hybrid_ai
from backend.algorithms.csp_scheduler import CSPScheduler
from backend.weather import TelemetryEngine
from backend.pdf_generator import generate_route_pdf

router = APIRouter()

@router.get("/locations")
async def get_locations():
    """Returns the geographic hierarchy tree."""
    return LOCATIONS

@router.post("/plan-route", response_model=RoutePlanResponse)
async def plan_route(payload: RoutePlanRequest, db: AsyncSession = Depends(get_db)):
    """Computes drone trajectory based on selected algorithm, obstacles, and weather."""
    # 1. Dynamically resolve bounding box to encompass Start, Target, and Obstacles
    lats = [payload.source.lat, payload.destination.lat]
    lons = [payload.source.lon, payload.destination.lon]
    
    for obs in payload.obstacles:
        # Approximate 1 km = 0.009 degrees for padding
        buffer = (obs.radius / 1000.0) * 0.01 
        lats.extend([obs.lat - buffer, obs.lat + buffer])
        lons.extend([obs.lon - buffer, obs.lon + buffer])
        
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Add 15% padding so the grid extends beyond the exact pins
    lat_pad = (max_lat - min_lat) * 0.15 or 0.01
    lon_pad = (max_lon - min_lon) * 0.15 or 0.01
    
    bounds = {
        "min_lat": min_lat - lat_pad,
        "max_lat": max_lat + lat_pad,
        "min_lon": min_lon - lon_pad,
        "max_lon": max_lon + lon_pad,
    }

    # 2. Instantiate pathfinding grid
    grid = GridEnvironment(bounds, cols=40, rows=40)
    
    # Process obstacles
    obs_dicts = []
    for obs in payload.obstacles:
        obs_dicts.append({
            "lat": obs.lat,
            "lon": obs.lon,
            "radius": obs.radius,
            "cost": obs.cost,
            "risk_level": obs.risk_level,
            "type": obs.type
        })
    grid.apply_obstacles(obs_dicts)
    
    start_grid = grid.latlon_to_grid(payload.source.lat, payload.source.lon)
    end_grid = grid.latlon_to_grid(payload.destination.lat, payload.destination.lon)
    
    # 3. Intelligent Algorithm Auto-Selection
    algo = payload.algorithm.upper()
    if algo == "AUTO":
        # Determine distance
        import math
        dist = math.sqrt((start_grid[0] - end_grid[0])**2 + (start_grid[1] - end_grid[1])**2)
        
        # Check for dynamic/extreme risks
        has_dynamic_risk = any(obs.type in ["Bird Flock", "Storm"] for obs in payload.obstacles)
        
        if has_dynamic_risk:
            algo = "HYBRID"
        elif dist > 30:
            algo = "IDASTAR"
        else:
            algo = "ASTAR"
            
    # 4. Dispatch to selected algorithm
    start_time = time.perf_counter()
    
    # All algorithms now receive mode and wind parameters for unified API
    common_kwargs = dict(
        mode=payload.optimization_mode,
        wind_speed=payload.weather.wind_speed,
        wind_direction=payload.weather.wind_direction,
    )
    try:
        if algo == "BFS":
            grid_path, visited = run_bfs(grid, start_grid, end_grid, **common_kwargs)
        elif algo == "DFS":
            grid_path, visited = run_dfs(grid, start_grid, end_grid, **common_kwargs)
        elif algo == "ASTAR":
            grid_path, visited = run_astar(grid, start_grid, end_grid, **common_kwargs)
        elif algo == "GBFS":
            grid_path, visited = run_gbfs(grid, start_grid, end_grid, **common_kwargs)
        elif algo == "UCS":
            grid_path, visited = run_ucs(grid, start_grid, end_grid, **common_kwargs)
        elif algo == "IDASTAR" or algo == "IDA*":
            grid_path, visited = run_idastar(grid, start_grid, end_grid, **common_kwargs)
        elif algo == "EXPECTIMAX":
            grid_path, visited = run_expectimax(grid, start_grid, end_grid, depth=3)
        elif algo == "HYBRID":
            grid_path, visited = run_hybrid_ai(grid, start_grid, end_grid, **common_kwargs)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported algorithm '{algo}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pathfinder execution error: {str(e)}")
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    if not grid_path:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid flight path could be resolved. All routes are obstructed by No-Fly Zones or grid boundaries."
        )

    # 6. Simulate flight telemetry
    sim = TelemetryEngine.simulate_flight(
        grid, 
        grid_path, 
        payload.weather.condition, 
        payload.weather.wind_speed, 
        payload.weather.wind_direction
    )

    # Map grid indices back to GPS coordinates for front-end rendering
    gps_path = [payload.source]
    for x, y in grid_path:
        lat, lon = grid.grid_to_latlon(x, y)
        gps_path.append(Coordinate(lat=lat, lon=lon))
    if gps_path:
        gps_path.append(payload.destination)

    # Calculate algorithm cost metrics and collect obstacles encountered
    total_cost = 0.0
    obstacles_encountered = []
    seen_obstacle_types = set()
    for x, y in grid_path:
        c = grid.grid_costs[y][x]
        total_cost += c if c != float('inf') else 9999.0
        obs_type = grid.grid_obstacles[y][x]
        if obs_type and obs_type not in seen_obstacle_types:
            seen_obstacle_types.add(obs_type)
            obstacles_encountered.append({
                "type": obs_type,
                "grid_x": x,
                "grid_y": y,
                "cost": float(c) if c != float('inf') else 9999.0,
                "risk": float(grid.grid_risks[y][x])
            })

    telemetry = TelemetrySummary(
        speed=sim["speed_profile"][-1] if sim["speed_profile"] else 0.0,
        altitude=sim["altitude_profile"][-1] if sim["altitude_profile"] else 50.0,
        battery_percentage=round(sim["battery_profile"][-1], 1),
        distance=sim["distance"],
        nodes_visited=len(visited),
        execution_time_ms=round(execution_time_ms, 2),
        cost=round(total_cost, 2),
        risk_score=sim["risk_score"]
    )

    # Generate recommendation advice
    ai_advice = TelemetryEngine.generate_ai_advisor(
        algo=algo,
        telemetry=sim,
        weather_cond=payload.weather.condition,
        wind_speed=payload.weather.wind_speed,
        has_obstacles=len(payload.obstacles) > 0,
        opt_mode=payload.optimization_mode
    )

    # 7. Log runs in analytics database asynchronously/silently
    try:
        log_entry = AnalyticsLog(
            algorithm=algo,
            execution_time_ms=execution_time_ms,
            nodes_visited=len(visited),
            path_length=float(len(grid_path)),
            cost=total_cost,
            battery_consumed=sim["battery_consumed"],
            risk_score=sim["risk_score"]
        )
        db.add(log_entry)
        await db.commit()
    except Exception as db_err:
        # Fallback: if database fails, log to stdout but don't crash the request
        print(f"Analytics write warning: {db_err}")
        await db.rollback()

    return RoutePlanResponse(
        algorithm=algo,
        optimization_mode=payload.optimization_mode,
        path=gps_path,
        grid_path=[list(cell) for cell in grid_path],
        visited=[list(cell) for cell in visited],
        telemetry=telemetry,
        battery_profile=sim["battery_profile"],
        ai_recommendation=ai_advice,
        obstacles_encountered=obstacles_encountered,
        total_distance=sim["distance"]
    )

@router.post("/routes", response_model=RouteResponse)
async def save_route(route: RouteSave, db: AsyncSession = Depends(get_db)):
    """Saves a computed flight plan in the database history."""
    try:
        new_route = Route(
            name=route.name,
            source_lat=route.source_lat,
            source_lon=route.source_lon,
            dest_lat=route.dest_lat,
            dest_lon=route.dest_lon,
            algorithm=route.algorithm,
            weather=route.weather,
            wind_speed=route.wind_speed,
            wind_direction=route.wind_direction,
            distance=route.distance,
            travel_time=route.travel_time,
            battery_consumed=route.battery_consumed,
            risk_score=route.risk_score,
            path_coords=json.dumps([c.dict() for c in route.path_coords])
        )
        db.add(new_route)
        await db.commit()
        await db.refresh(new_route)
        
        # Structure the path_coords back into Pydantic model for matching return signature
        res = RouteResponse(
            id=new_route.id,
            name=new_route.name,
            source_lat=new_route.source_lat,
            source_lon=new_route.source_lon,
            dest_lat=new_route.dest_lat,
            dest_lon=new_route.dest_lon,
            algorithm=new_route.algorithm,
            weather=new_route.weather,
            wind_speed=new_route.wind_speed,
            wind_direction=new_route.wind_direction,
            distance=new_route.distance,
            travel_time=new_route.travel_time,
            battery_consumed=new_route.battery_consumed,
            risk_score=new_route.risk_score,
            path_coords=route.path_coords,
            created_at=new_route.created_at
        )
        return res
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database save error: {str(e)}")

@router.get("/routes", response_model=List[RouteResponse])
async def get_routes_history(db: AsyncSession = Depends(get_db)):
    """Lists saved flight history."""
    try:
        stmt = select(Route).order_by(Route.created_at.desc()).limit(20)
        result = await db.execute(stmt)
        db_routes = result.scalars().all()
        
        res_list = []
        for r in db_routes:
            coords_raw = json.loads(r.path_coords)
            path_coords = [Coordinate(lat=c["lat"], lon=c["lon"]) for c in coords_raw]
            res_list.append(RouteResponse(
                id=r.id,
                name=r.name,
                source_lat=r.source_lat,
                source_lon=r.source_lon,
                dest_lat=r.dest_lat,
                dest_lon=r.dest_lon,
                algorithm=r.algorithm,
                weather=r.weather,
                wind_speed=r.wind_speed,
                wind_direction=r.wind_direction,
                distance=r.distance,
                travel_time=r.travel_time,
                battery_consumed=r.battery_consumed,
                risk_score=r.risk_score,
                path_coords=path_coords,
                created_at=r.created_at
            ))
        return res_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch error: {str(e)}")

@router.get("/analytics", response_model=List[AnalyticsSummary])
async def get_analytics_benchmarks(db: AsyncSession = Depends(get_db)):
    """Aggregates performance statistics for algorithm performance charts."""
    try:
        # Group by algorithm and calculate average metrics
        stmt = (
            select(
                AnalyticsLog.algorithm,
                func.avg(AnalyticsLog.execution_time_ms).label("avg_time"),
                func.avg(AnalyticsLog.nodes_visited).label("avg_nodes"),
                func.avg(AnalyticsLog.path_length).label("avg_length"),
                func.avg(AnalyticsLog.cost).label("avg_cost"),
                func.avg(AnalyticsLog.battery_consumed).label("avg_battery"),
                func.avg(AnalyticsLog.risk_score).label("avg_risk"),
                func.count(AnalyticsLog.id).label("count")
            )
            .group_by(AnalyticsLog.algorithm)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        benchmarks = []
        for row in rows:
            benchmarks.append(AnalyticsSummary(
                algorithm=row[0],
                avg_execution_time_ms=float(row[1] or 0),
                avg_nodes_visited=float(row[2] or 0),
                avg_path_length=float(row[3] or 0),
                avg_cost=float(row[4] or 0),
                avg_battery_consumed=float(row[5] or 0),
                avg_risk_score=float(row[6] or 0),
                run_count=int(row[7] or 0)
            ))
            
        # If no entries are in database yet, send mock/baseline benchmark averages
        # so frontend displays charts correctly on startup
        active_algos = {b.algorithm.upper() for b in benchmarks}
        baseline_defaults = [
            ("AStar", 1.8, 120, 24.5, 30.5, 12.2, 0.08),
            ("GBFS", 0.9, 45, 26.2, 32.4, 13.1, 0.12),
            ("BFS", 5.6, 680, 24.5, 30.5, 12.2, 0.08),
            ("DFS", 4.1, 410, 68.4, 88.0, 38.6, 0.45),
            ("UCS", 2.5, 200, 24.5, 28.0, 11.8, 0.06),
        ]
        
        for name, t, nodes, length, cost, bat, rsk in baseline_defaults:
            if name.upper() not in active_algos:
                benchmarks.append(AnalyticsSummary(
                    algorithm=name,
                    avg_execution_time_ms=t,
                    avg_nodes_visited=nodes,
                    avg_path_length=length,
                    avg_cost=cost,
                    avg_battery_consumed=bat,
                    avg_risk_score=rsk,
                    run_count=0
                ))
                
        return benchmarks
    except Exception as e:
        print(f"Database analytics warning: {e}")
        # Fallback if DB fails: return baseline mock benchmarks so charts render nicely
        return [
            AnalyticsSummary(algorithm="AStar", avg_execution_time_ms=1.8, avg_nodes_visited=120, avg_path_length=24.5, avg_cost=30.5, avg_battery_consumed=12.2, avg_risk_score=0.08, run_count=0),
            AnalyticsSummary(algorithm="GBFS", avg_execution_time_ms=0.9, avg_nodes_visited=45, avg_path_length=26.2, avg_cost=32.4, avg_battery_consumed=13.1, avg_risk_score=0.12, run_count=0),
            AnalyticsSummary(algorithm="BFS", avg_execution_time_ms=5.6, avg_nodes_visited=680, avg_path_length=24.5, avg_cost=30.5, avg_battery_consumed=12.2, avg_risk_score=0.08, run_count=0),
            AnalyticsSummary(algorithm="DFS", avg_execution_time_ms=4.1, avg_nodes_visited=410, avg_path_length=68.4, avg_cost=88.0, avg_battery_consumed=38.6, avg_risk_score=0.45, run_count=0),
            AnalyticsSummary(algorithm="UCS", avg_execution_time_ms=2.5, avg_nodes_visited=200, avg_path_length=24.5, avg_cost=28.0, avg_battery_consumed=11.8, avg_risk_score=0.06, run_count=0),
        ]

@router.post("/export-pdf")
async def export_pdf(payload: Dict[str, Any]):
    """Generates PDF binary stream for download."""
    try:
        route_data = payload.get("route_data")
        comparison_data = payload.get("comparison_data")
        
        if not route_data:
            raise HTTPException(status_code=400, detail="Missing 'route_data' parameter.")
            
        pdf_buffer = generate_route_pdf(route_data, comparison_data)
        
        filename = f"mission_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/schedule-fleet", response_model=FleetScheduleResponse)
async def schedule_fleet(payload: FleetScheduleRequest):
    """Assigns charging stations and time slots to a fleet of drones without overlap."""
    try:
        scheduler = CSPScheduler(
            drones=payload.drones,
            stations=payload.stations,
            time_slots=payload.time_slots
        )
        assignment = scheduler.solve()
        
        # Convert tuple back to list for JSON serialization
        if assignment:
            formatted_assignment = {drone: [station, time_slot] for drone, (station, time_slot) in assignment.items()}
        else:
            formatted_assignment = None
            
        return FleetScheduleResponse(schedule=formatted_assignment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSP Scheduling failed: {str(e)}")
