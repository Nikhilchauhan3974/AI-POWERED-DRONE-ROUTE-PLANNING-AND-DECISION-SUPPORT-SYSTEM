import math
from typing import List, Tuple, Dict, Any

class TelemetryEngine:
    DRONE_BASE_SPEED_MPS = 13.89  # 50 km/h in m/s
    BATTERY_DRAIN_PER_METER = 0.005  # 100% battery covers ~20 km in clear conditions
    
    @staticmethod
    def get_weather_modifiers(condition: str) -> Dict[str, float]:
        """Returns speed, battery, and risk multipliers for different weather states."""
        cond = condition.lower()
        if cond == "rain":
            return {"speed": 0.8, "battery": 1.25, "risk": 1.3}
        elif cond == "wind":
            return {"speed": 0.9, "battery": 1.15, "risk": 1.2}
        elif cond == "fog":
            return {"speed": 0.6, "battery": 1.0, "risk": 1.7}
        elif cond == "storm":
            return {"speed": 0.5, "battery": 1.5, "risk": 2.2}
        else:  # clear
            return {"speed": 1.0, "battery": 1.0, "risk": 1.0}

    @classmethod
    def simulate_flight(
        cls, 
        grid, 
        grid_path: List[Tuple[int, int]], 
        weather_cond: str, 
        wind_speed: float, 
        wind_direction: float
    ) -> Dict[str, Any]:
        """Simulates drone physics along a grid path to generate realistic telemetry."""
        if not grid_path:
            return {
                "distance": 0.0,
                "travel_time": 0.0,
                "battery_consumed": 0.0,
                "risk_score": 0.0,
                "battery_profile": [],
                "altitude_profile": [],
                "speed_profile": []
            }

        weather = cls.get_weather_modifiers(weather_cond)
        
        # Wind vector conversion
        wind_rad = math.radians(wind_direction)
        wx = math.sin(wind_rad)
        wy = math.cos(wind_rad)
        wind_intensity = min(wind_speed / 60.0, 1.0)  # Max 60 km/h wind is 1.0 intensity

        total_distance = 0.0
        total_time = 0.0
        current_battery = 100.0
        battery_profile = [current_battery]
        
        current_altitude = 50.0  # Cruise baseline
        altitude_profile = [current_altitude]
        
        speed_profile = [0.0]  # Starting from rest
        total_risk = 0.0
        
        for i in range(len(grid_path) - 1):
            x1, y1 = grid_path[i]
            x2, y2 = grid_path[i+1]
            
            # Distance in meters
            lat1, lon1 = grid.grid_to_latlon(x1, y1)
            lat2, lon2 = grid.grid_to_latlon(x2, y2)
            d = haversine_distance(lat1, lon1, lat2, lon2)
            total_distance += d

            # Target cell details
            cell_cost = grid.grid_costs[y2][x2]
            cell_risk = grid.grid_risks[y2][x2]
            cell_obstacle = grid.grid_obstacles[y2][x2]

            # Altitude logic based on obstacle type
            target_alt = 50.0  # Cruise
            if cell_obstacle:
                obs = cell_obstacle.lower()
                if "mountain" in obs:
                    target_alt = 130.0
                elif "skyscraper" in obs:
                    target_alt = 100.0
                elif "electric tower" in obs:
                    target_alt = 70.0
                elif "trees" in obs:
                    target_alt = 35.0
                elif "aircraft" in obs:
                    target_alt = 160.0

            # Altitude energy penalty
            climb_penalty = 1.0
            speed_penalty = 1.0
            if target_alt > current_altitude:
                # Climbing: uses 1.8x energy, reduces speed by 30%
                climb_penalty = 1.8
                speed_penalty = 0.7
                current_altitude = target_alt
            elif target_alt < current_altitude:
                # Descending: slightly helps energy, standard speed
                climb_penalty = 0.9
                current_altitude = target_alt
            
            # Wind vector projection
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                tx, ty = dx / length, dy / length
                wind_dot = tx * wx + ty * wy
            else:
                wind_dot = 0

            # Wind impact
            # Tailwind increases speed (up to +25%) and reduces battery drain (down to -20%)
            # Headwind decreases speed (down to -35%) and increases battery drain (up to +45%)
            speed_wind_mult = 1.0 + (0.25 * wind_dot * wind_intensity)
            speed_wind_mult = max(0.65, min(1.25, speed_wind_mult))
            
            battery_wind_mult = 1.0 - (0.2 * wind_dot * wind_intensity)
            battery_wind_mult = max(0.8, min(1.45, battery_wind_mult))

            # Step Speed
            step_speed = cls.DRONE_BASE_SPEED_MPS * weather["speed"] * speed_wind_mult * speed_penalty
            step_speed = max(3.0, min(22.0, step_speed))  # Keep within limits
            speed_profile.append(step_speed * 3.6)  # Store in km/h

            # Step Time
            step_time = d / step_speed
            total_time += step_time

            # Step Battery Drain
            step_drain = (d * cls.BATTERY_DRAIN_PER_METER * 
                          weather["battery"] * 
                          battery_wind_mult * 
                          climb_penalty)
            
            # Navigating high-cost zones draws more stabilization power
            if cell_cost != float('inf') and cell_cost > 1.0:
                step_drain *= (1.0 + (cell_cost - 1.0) * 0.15)
                
            current_battery = max(0.0, current_battery - step_drain)
            battery_profile.append(current_battery)
            altitude_profile.append(current_altitude)

            # Step Risk Accumulation
            step_risk = cell_risk * weather["risk"]
            total_risk += step_risk * (d / 100.0)  # scale risk by distance traversed in risk cells

        # Calculate average risk over route
        route_risk = min(1.0, total_risk / (total_distance / 200.0 + 1.0) if total_distance > 0 else 0)

        return {
            "distance": round(total_distance, 1),
            "travel_time": round(total_time, 1),
            "battery_consumed": round(100.0 - current_battery, 1),
            "risk_score": round(route_risk, 3),
            "battery_profile": [round(b, 2) for b in battery_profile],
            "altitude_profile": [round(a, 1) for a in altitude_profile],
            "speed_profile": [round(s, 1) for s in speed_profile]
        }

    @staticmethod
    def generate_ai_advisor(
        algo: str, 
        telemetry: Dict[str, Any], 
        weather_cond: str, 
        wind_speed: float, 
        has_obstacles: bool, 
        opt_mode: str
    ) -> str:
        """Rule-based AI Expert System that generates high-context routing recommendations."""
        algo_name = algo.upper()
        weather = weather_cond.lower()
        battery_used = telemetry["battery_consumed"]
        risk = telemetry["risk_score"]
        dist = telemetry["distance"]
        
        tips = []
        
        # 1. Evaluate algorithm choice
        if algo_name in ["BFS", "DFS"]:
            tips.append(f"CRITICAL: {algo_name} is an unweighted search. It does NOT evaluate wind vector gradients or obstacle risk elevations, leading to sub-optimal pathing.")
            if risk > 0.4:
                tips.append("Recommendation: Switch to A* (Safe Mode) or UCS to reroute around hazardous nodes.")
            elif battery_used > 50:
                tips.append("Recommendation: Switch to A* (Eco Mode) or UCS (Eco Mode) to leverage wind assistance and reduce power drain.")
        elif algo_name == "GBFS":
            tips.append("ANALYSIS: Greedy Best-First Search is fast but heuristic-driven. It operates on line-of-sight grids, which often results in local-minima deviations in cluttered zones.")
        elif algo_name == "UCS":
            tips.append(f"ANALYSIS: Uniform Cost Search (Dijkstra) guarantees minimum-cost path by expanding nodes in order of cumulative cost g(n). Currently in [{opt_mode}] mode.")
            if len(tips) == 1:
                tips.append("UCS is optimal for cost-sensitive missions. It explores more nodes than A* but guarantees the global minimum-cost solution.")
        elif algo_name == "ASTAR":
            tips.append(f"ANALYSIS: A* Search is actively optimizing for dynamic variables. Currently operating in [{opt_mode}] optimization mode.")
            
        # 2. Evaluate Weather & Wind
        if weather == "storm":
            tips.append("WEATHER WARNING: Active Storm detected. Traversal costs are scaled by 1.5x, and drone speeds are halved. Ensure battery reserve is above 40%.")
        elif weather == "fog":
            tips.append("VISIBILITY ALERT: Dense fog raises collision risk index. Pathfinding has applied safety margins to obstacle clearance distances.")
        elif weather == "wind" and wind_speed > 25:
            tips.append(f"WIND SENSORS: High wind speed ({wind_speed} km/h) active. Recommend utilizing A* Eco Mode to minimize headwind drag vectors.")
            
        # 3. Evaluate Telemetry
        if battery_used > 85:
            tips.append(f"BATTERY DANGER: Estimated mission power usage ({battery_used}%) exceeds safety margins. Drone will run out of charge before arriving!")
        elif battery_used > 70:
            tips.append(f"BATTERY WARNING: High consumption ({battery_used}%). Reroute with fewer climbing segments or land/recharge midway.")
            
        if risk > 0.6:
            tips.append(f"HAZARD WARNING: Route risk score ({round(risk * 100)}%) is high. The flight plan traverses active No-Fly boundaries or Storm Centers.")
        elif risk > 0.2 and risk <= 0.6:
            tips.append("FLIGHT ADVISORY: Path traverses moderate risk zones. Telemetry monitors skyscrapers and electric lines.")

        if not tips:
            tips.append("SYSTEM STATE: Nominal. Route is fully optimized. Clear weather allows standard cruise profile.")

        return " | ".join(tips)

# Duplicate the helper here to keep it self-contained
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
