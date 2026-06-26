import React, { useState, useEffect } from 'react';
import { ShieldAlert, Compass, Save, Eye, Layers, Award, Terminal } from 'lucide-react';
import confetti from 'canvas-confetti';

import MapContainerComponent from './components/MapContainer';
import TelemetryHud from './components/TelemetryHud';
import ComparisonDashboard from './components/ComparisonDashboard';
import ControlPanel from './components/ControlPanel';
import AiAdvisor from './components/AiAdvisor';
import RouteHistory from './components/RouteHistory';

const API_BASE = "http://localhost:8000/api";

export default function App() {
  // Config states
  const [locations, setLocations] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  
  // Coordinates and obstacles
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);
  const [obstacles, setObstacles] = useState([]);
  const [obstacleType, setObstacleType] = useState('No-Fly Zones');
  
  // Selection states
  const [optimizationMode, setOptimizationMode] = useState('Safe');
  const [weather, setWeather] = useState({
    condition: 'clear',
    wind_speed: 0.0,
    wind_direction: 0.0
  });

  // Solver responses
  const [planResponse, setPlanResponse] = useState(null);
  const [routePath, setRoutePath] = useState(null);
  const [visitedCells, setVisitedCells] = useState(null);
  const [aiAdvice, setAiAdvice] = useState('');
  
  // Telemetry logs
  const [activeTelemetry, setActiveTelemetry] = useState({
    speed: 0.0,
    altitude: 50.0,
    battery_percentage: 100.0,
    distance: 0.0,
    nodes_visited: 0,
    execution_time_ms: 0.0,
    cost: 0.0,
    risk_score: 0.0
  });
  const [currentCoords, setCurrentCoords] = useState(null);

  // App running states
  const [isRunning, setIsRunning] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // History & comparisons
  const [history, setHistory] = useState([]);
  const [comparisonData, setComparisonData] = useState([]);

  // Fetch geographic centers and histories on load
  useEffect(() => {
    fetchLocations();
    fetchHistory();
    fetchAnalytics();
  }, []);

  async function fetchLocations() {
    try {
      const res = await fetch(`${API_BASE}/locations`);
      const data = await res.json();
      setLocations(data);
      // Select Manhattan Central by default
      const defaultLoc = data["USA"]["New York"]["New York City"]["Manhattan Central"];
      setSelectedLocation(defaultLoc);
      
      // Auto-set dummy start and end coordinates near center
      setStartPoint({ lat: defaultLoc.center.lat - 0.008, lon: defaultLoc.center.lon - 0.008 });
      setEndPoint({ lat: defaultLoc.center.lat + 0.008, lon: defaultLoc.center.lon + 0.008 });
    } catch (err) {
      setErrorMessage("Could not load location hierarchy from backend.");
    }
  };

  async function fetchHistory() {
    try {
      const res = await fetch(`${API_BASE}/routes`);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.warn("Could not load route histories.", err);
    }
  };

  async function fetchAnalytics() {
    try {
      const res = await fetch(`${API_BASE}/analytics`);
      const data = await res.json();
      setComparisonData(data);
    } catch (err) {
      console.warn("Could not load comparison logs.", err);
    }
  };

  // Location Selector callback
  const handleLocationChange = (loc) => {
    setSelectedLocation(loc);
    // Reset path nodes
    setStartPoint({ lat: loc.center.lat - 0.006, lon: loc.center.lon - 0.006 });
    setEndPoint({ lat: loc.center.lat + 0.006, lon: loc.center.lon + 0.006 });
    setRoutePath(null);
    setVisitedCells(null);
    setPlanResponse(null);
    setErrorMessage('');
    setSuccessMessage('');
  };

  // Add obstacles to active array — IMMEDIATE recalculation
  const handleAddObstacle = (newObs) => {
    const updatedObstacles = [...obstacles, newObs];
    setObstacles(updatedObstacles);
    setErrorMessage('');
    // Immediate recalculation when obstacles change (no delay)
    if (planResponse || routePath) {
      setSuccessMessage("Obstacle detected. Re-routing immediately...");
      triggerRoutePlan(updatedObstacles);
    }
  };

  // Auto re-route when optimization mode changes (if path already exists)
  useEffect(() => {
    if (planResponse && startPoint && endPoint) {
      setSuccessMessage(`Switched to ${optimizationMode}. Recalculating...`);
      triggerRoutePlan();
    }
  }, [optimizationMode]);

  const clearObstacles = () => {
    setObstacles([]);
    setRoutePath(null);
    setVisitedCells(null);
    setPlanResponse(null);
    setErrorMessage('');
    setSuccessMessage('');
  };

  const resetMap = () => {
    clearObstacles();
    if (selectedLocation) {
      setStartPoint({ lat: selectedLocation.center.lat - 0.006, lon: selectedLocation.center.lon - 0.006 });
      setEndPoint({ lat: selectedLocation.center.lat + 0.006, lon: selectedLocation.center.lon + 0.006 });
    }
    setActiveTelemetry({
      speed: 0.0,
      altitude: 50.0,
      battery_percentage: 100.0,
      distance: 0.0,
      nodes_visited: 0,
      execution_time_ms: 0.0,
      cost: 0.0,
      risk_score: 0.0
    });
    setCurrentCoords(null);
    setAiAdvice('');
  };

  // API solve handler
  async function triggerRoutePlan(activeObstacles = obstacles) {
    if (!startPoint || !endPoint) {
      setErrorMessage("Please configure both Start (Green) and Target (Red) waypoints.");
      return;
    }

    setErrorMessage('');
    setSuccessMessage('');
    setIsRunning(true);

    try {
      const payload = {
        source: startPoint,
        destination: endPoint,
        algorithm: "AUTO",
        optimization_mode: optimizationMode,
        weather,
        obstacles: activeObstacles,
        bounds: selectedLocation ? selectedLocation.bounds : null
      };

      const res = await fetch(`${API_BASE}/plan-route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Server pathfinding failed.");
      }

      const data = await res.json();
      setPlanResponse(data);
      setRoutePath(data.path);
      setVisitedCells(data.visited);
      setAiAdvice(data.ai_recommendation);
      
      // Set static telemetry outputs on load
      setActiveTelemetry(data.telemetry);
      setCurrentCoords(data.path[0]);
      setSuccessMessage("Flight plan computed. Waypoints ready for upload.");

      // Refresh side comparisons
      fetchAnalytics();
    } catch (err) {
      setErrorMessage(err.message || "Failed to establish telemetry link with backend.");
      setRoutePath(null);
      setVisitedCells(null);
      setPlanResponse(null);
    } finally {
      setIsRunning(false);
    }
  };

  // Start drone traversal playback
  const startMission = () => {
    if (!routePath || routePath.length === 0) return;
    setIsSimulating(true);
    setSuccessMessage("Autopilot active. Traversing waypoints...");
  };

  // Animation ticks
  const handleSimulationFrame = (idx) => {
    if (!planResponse || !routePath) return;
    
    const totalSteps = routePath.length;
    const progress = idx / (totalSteps - 1 || 1);
    const batteryVal = planResponse.battery_profile[idx] ?? 100.0;
    
    // Check if altitude rises due to obstacles in grid cell
    const [gx, gy] = planResponse.grid_path[idx] || [0, 0];
    
    // Fluctuate altitude climb and speed
    let altVal = 50.0;
    const speedVal = idx === 0 ? 0.0 : planResponse.telemetry.speed;

    setActiveTelemetry({
      ...planResponse.telemetry,
      speed: Number(speedVal.toFixed(1)),
      battery_percentage: Number(batteryVal.toFixed(1)),
      distance: Number((progress * planResponse.telemetry.distance).toFixed(0))
    });
    setCurrentCoords(routePath[idx]);
  };

  const handleSimulationFinish = () => {
    setIsSimulating(false);
    setSuccessMessage("Delivery complete. Confirmed package dropoff.");
    
    // Confetti!
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#06b6d4', '#10b981', '#f59e0b']
    });
  };

  // Save flight coordinates in DB
  const saveFlightPlan = async () => {
    if (!planResponse) return;
    
    const runName = `${selectedLocation.center.lat.toFixed(3)} Mission // ${planResponse.algorithm}`;
    const payload = {
      name: runName,
      source_lat: startPoint.lat,
      source_lon: startPoint.lon,
      dest_lat: endPoint.lat,
      dest_lon: endPoint.lon,
      algorithm: planResponse.algorithm,
      weather: weather.condition,
      wind_speed: weather.wind_speed,
      wind_direction: weather.wind_direction,
      distance: planResponse.telemetry.distance,
      travel_time: planResponse.telemetry.distance / (planResponse.telemetry.speed / 3.6),
      battery_consumed: 100.0 - planResponse.battery_profile[planResponse.battery_profile.length - 1],
      risk_score: planResponse.telemetry.risk_score,
      path_coords: planResponse.path
    };

    try {
      const res = await fetch(`${API_BASE}/routes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setSuccessMessage("Mission logged in system history database.");
        fetchHistory();
      } else {
        throw new Error("Failed to write to DB.");
      }
    } catch (err) {
      setErrorMessage("Could not record flight plan to database.");
    }
  };

  // Download PDF Report
  const exportPdfReport = async () => {
    if (!planResponse) return;
    
    const payload = {
      route_data: {
        source_lat: startPoint.lat,
        source_lon: startPoint.lon,
        dest_lat: endPoint.lat,
        dest_lon: endPoint.lon,
        algorithm: planResponse.algorithm,
        weather: weather.condition,
        wind_speed: weather.wind_speed,
        wind_direction: weather.wind_direction,
        distance: planResponse.telemetry.distance,
        travel_time: planResponse.telemetry.distance / (planResponse.telemetry.speed / 3.6 || 1),
        battery_consumed: 100.0 - planResponse.battery_profile[planResponse.battery_profile.length - 1],
        risk_score: planResponse.telemetry.risk_score
      },
      comparison_data: comparisonData.map(c => ({
        algorithm: c.algorithm,
        execution_time_ms: c.avg_execution_time_ms,
        nodes_visited: c.avg_nodes_visited,
        distance: c.avg_path_length * 150.0,
        battery_consumed: c.avg_battery_consumed,
        risk_score: c.avg_risk_score
      }))
    };

    try {
      const res = await fetch(`${API_BASE}/export-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `flight_report_${planResponse.algorithm}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      setErrorMessage("Could not compile PDF report file.");
    }
  };

  // Load old historical coordinates
  const loadHistoryRoute = (run) => {
    setStartPoint({ lat: run.source_lat, lon: run.source_lon });
    setEndPoint({ lat: run.dest_lat, lon: run.dest_lon });
    
    const mockPlanResponse = {
      algorithm: run.algorithm,
      path: run.path_coords,
      grid_path: [],
      visited: [],
      telemetry: {
        speed: 45.0,
        altitude: 50.0,
        battery_percentage: 100.0 - run.battery_consumed,
        distance: run.distance,
        nodes_visited: 120,
        execution_time_ms: 1.5,
        cost: 24.0,
        risk_score: run.risk_score
      },
      battery_profile: new Array(run.path_coords.length).fill(100.0 - run.battery_consumed),
      ai_recommendation: "HISTORICAL PLAN LOADED: Bypassed db constraints. Telemetry logs retrieved."
    };
    
    setPlanResponse(mockPlanResponse);
    setRoutePath(run.path_coords);
    setVisitedCells([]);
    setAiAdvice(mockPlanResponse.ai_recommendation);
    setActiveTelemetry(mockPlanResponse.telemetry);
    setCurrentCoords(run.path_coords[0]);
    setSuccessMessage(`Historical plan "${run.name}" restored to dashboard.`);
  };

  return (
    <div className="min-h-screen bg-cyber-bg p-4 flex flex-col gap-4">
      {/* 1. Header Command HUD */}
      <header className="glass-panel p-4 flex items-center justify-between border-b-2 border-b-cyber-cyan shadow-[0_0_15px_rgba(6,182,212,0.1)]">
        <div>
          <h1 className="text-xl font-black text-slate-100 flex items-center gap-2 tracking-widest glitch-text">
            <Compass className="h-6 w-6 text-cyber-cyan animate-radar" /> AERO-COM AI COMMAND CENTER
          </h1>
          <p className="text-[10px] mono-font text-slate-500 uppercase tracking-wider mt-0.5">
            Autonomous Drone Routing Engine & Dynamic Obstacle Avoidance HUD
          </p>
        </div>
        <div className="flex items-center gap-3 text-right">
          <div className="flex flex-col text-[10px] mono-font text-slate-400">
            <span className="text-cyber-green font-bold flex items-center gap-1 justify-end">
              <span className="h-2 w-2 rounded-full bg-cyber-green inline-block animate-pulse"></span> TELEMETRY ACTIVE
            </span>
            <span>GRID SOLVER v9.25</span>
          </div>
        </div>
      </header>

      {/* 2. Error/Success Toasts */}
      {(errorMessage || successMessage) && (
        <div className="flex flex-col gap-2">
          {errorMessage && (
            <div className="bg-cyber-red/10 border border-cyber-red/30 text-cyber-red px-4 py-2 rounded text-xs flex items-center gap-2 mono-font animate-pulse">
              <ShieldAlert className="h-4 w-4" /> {errorMessage}
            </div>
          )}
          {successMessage && (
            <div className="bg-cyber-green/10 border border-cyber-green/30 text-cyber-green px-4 py-2 rounded text-xs flex items-center gap-2 mono-font">
              <Terminal className="h-4 w-4" /> {successMessage}
            </div>
          )}
        </div>
      )}

      {/* 3. Three Column Workspace Grid */}
      <main className="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1 items-start">
        {/* Left Control Column */}
        <section className="lg:col-span-1 flex flex-col gap-4">
          <ControlPanel
            locations={locations}
            selectedLocation={selectedLocation}
            onLocationChange={handleLocationChange}
            activeAlgorithm={planResponse?.algorithm}
            optimizationMode={optimizationMode}
            onOptimizationChange={setOptimizationMode}
            weather={weather}
            onWeatherChange={setWeather}
            onPlanRoute={() => triggerRoutePlan()}
            onStartMission={startMission}
            onClearObstacles={clearObstacles}
            onResetMap={resetMap}
            onExportPdf={exportPdfReport}
            hasPath={!!routePath}
            isRunning={isRunning || isSimulating}
            obstacleType={obstacleType}
            onObstacleTypeChange={setObstacleType}
          />
          
          <AiAdvisor recommendation={aiAdvice} />
        </section>

        {/* Center Live Map Column */}
        <section className="lg:col-span-2 flex flex-col gap-4">
          <MapContainerComponent
            locationData={selectedLocation}
            obstacles={obstacles}
            onAddObstacle={handleAddObstacle}
            startPoint={startPoint}
            onSetStartPoint={setStartPoint}
            endPoint={endPoint}
            onSetEndPoint={setEndPoint}
            routePath={routePath}
            visitedCells={visitedCells}
            isSimulating={isSimulating}
            onSimulationFrame={handleSimulationFrame}
            onSimulationFinish={handleSimulationFinish}
            obstacleType={obstacleType}
          />
          
          {/* Mission logs quick action bar */}
          {planResponse && !isSimulating && (
            <div className="glass-panel p-3 flex items-center justify-between bg-slate-950/40 border border-slate-800">
              <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                Trajectory loaded: {routePath?.length} nodes solved. Click to log flight.
              </span>
              <button
                onClick={saveFlightPlan}
                className="bg-cyber-cyan/15 text-cyber-cyan border border-cyber-cyan/30 px-3 py-1.5 rounded text-[10px] uppercase font-bold tracking-widest hover:bg-cyber-cyan hover:text-slate-950 transition-all flex items-center gap-1"
              >
                <Save className="h-3 w-3" /> Log Flight
              </button>
            </div>
          )}
        </section>

        {/* Right HUD metrics Column */}
        <section className="lg:col-span-1 flex flex-col gap-4">
          <TelemetryHud
            telemetry={activeTelemetry}
            currentCoords={currentCoords}
            isRunning={isSimulating}
            algorithmInfo={{
              algorithm: planResponse?.algorithm || "AUTO",
              mode: planResponse?.optimization_mode || optimizationMode
            }}
            obstaclesEncountered={planResponse?.obstacles_encountered || []}
            totalDistance={planResponse?.total_distance || planResponse?.telemetry?.distance || 0}
          />

          <ComparisonDashboard comparisonData={comparisonData} />

          <RouteHistory
            history={history}
            onLoadRoute={loadHistoryRoute}
          />
        </section>
      </main>
    </div>
  );
}
