import React, { useState, useEffect } from 'react';
import { Compass, Play, RotateCcw, AlertOctagon, CloudSun, Eye, FileText, Globe, Cpu } from 'lucide-react';

export default function ControlPanel({
  locations,
  selectedLocation,
  onLocationChange,
  activeAlgorithm,
  optimizationMode,
  onOptimizationChange,
  weather,
  onWeatherChange,
  onPlanRoute,
  onStartMission,
  onClearObstacles,
  onResetMap,
  onExportPdf,
  hasPath,
  isRunning,
  obstacleType,
  onObstacleTypeChange
}) {
  const getObstacleColor = (type) => {
    const colors = {
      "No-Fly Zones": "text-cyber-red border-cyber-red bg-cyber-red/10",
      "Skyscrapers": "text-pink-500 border-pink-500 bg-pink-500/10",
      "Mountains": "text-orange-500 border-orange-500 bg-orange-500/10",
      "Storm Zones": "text-purple-500 border-purple-500 bg-purple-500/10",
      "Electric Towers": "text-yellow-500 border-yellow-500 bg-yellow-500/10",
      "Bird Flocks": "text-teal-400 border-teal-400 bg-teal-400/10",
      "Other Drones": "text-indigo-400 border-indigo-400 bg-indigo-400/10",
      "Aircraft": "text-rose-500 border-rose-500 bg-rose-500/10",
      "Communication Blackout Zones": "text-slate-400 border-slate-400 bg-slate-400/10",
      "Trees": "text-emerald-500 border-emerald-500 bg-emerald-500/10",
    };
    return colors[type] || "text-cyber-cyan border-cyber-cyan";
  };

  const formatAlgorithmName = (algo) => {
    if (!algo) return "AWAITING MISSION...";
    const names = {
      "ASTAR": "A* Algorithm",
      "IDASTAR": "IDA* Algorithm",
      "GBFS": "Greedy Best-First Search",
      "HYBRID": "Hybrid AI (Expectimax + HMM)",
      "EXPECTIMAX": "Expectimax Search",
      "BFS": "Breadth-First Search",
      "DFS": "Depth-First Search",
      "UCS": "Uniform Cost Search"
    };
    return names[algo] || algo;
  };

  const getAlgorithmReasoning = (algo) => {
    if (!algo) return "Waiting for parameters to decide best routing approach...";
    const reasons = {
      "ASTAR": "Selected for general-purpose mathematically guaranteed optimal pathfinding.",
      "IDASTAR": "Selected to conserve memory usage over a very long distance.",
      "GBFS": "Selected for maximum computational speed, sacrificing fuel efficiency.",
      "HYBRID": "Selected to dynamically evade unpredictable, stochastic threats."
    };
    return reasons[algo] || "System selected standard heuristic route.";
  };

  // Local state for hierarchical location selection
  const [selectedCountry, setSelectedCountry] = useState('USA');
  const [selectedState, setSelectedState] = useState('New York');
  const [selectedDistrict, setSelectedDistrict] = useState('New York City');
  const [selectedCity, setSelectedCity] = useState('Manhattan Central');

  // Trigger location update on change
  useEffect(() => {
    if (locations && locations[selectedCountry]?.[selectedState]?.[selectedDistrict]?.[selectedCity]) {
      onLocationChange(locations[selectedCountry][selectedState][selectedDistrict][selectedCity]);
    }
  }, [selectedCountry, selectedState, selectedDistrict, selectedCity, locations]);

  // Handle weather changes
  const handleWeatherConditionChange = (condition) => {
    let windSpeed = 0;
    let windDir = 0;

    if (condition === 'wind') {
      windSpeed = 35;
      windDir = 90; // East
    } else if (condition === 'storm') {
      windSpeed = 55;
      windDir = 180; // South
    } else if (condition === 'rain') {
      windSpeed = 15;
      windDir = 45;
    } else if (condition === 'fog') {
      windSpeed = 5;
      windDir = 0;
    }

    onWeatherChange({
      condition,
      wind_speed: windSpeed,
      wind_direction: windDir
    });
  };



  return (
    <div className="glass-panel p-4 border-t-2 border-t-cyber-cyan shadow-[0_0_15px_rgba(6,182,212,0.15)] flex flex-col gap-4">
      {/* 1. Geographical Location Selector */}
      <div>
        <label className="text-[10px] uppercase font-bold text-slate-500 flex items-center gap-1.5 tracking-widest mb-1.5">
          <Globe className="h-3 w-3 text-cyber-cyan" /> GEO-TRACKING COORDINATES
        </label>
        <div className="grid grid-cols-2 gap-2">
          <select
            value={selectedCountry}
            onChange={(e) => {
              setSelectedCountry(e.target.value);
              const states = Object.keys(locations[e.target.value]);
              setSelectedState(states[0]);
              const dists = Object.keys(locations[e.target.value][states[0]]);
              setSelectedDistrict(dists[0]);
              const cities = Object.keys(locations[e.target.value][states[0]][dists[0]]);
              setSelectedCity(cities[0]);
            }}
            className="bg-slate-900 border border-slate-800 text-[11px] rounded p-1.5 focus:outline-none focus:border-cyber-cyan text-slate-300 font-semibold cursor-pointer"
          >
            {locations ? Object.keys(locations).map(c => <option key={c} value={c}>{c}</option>) : <option>Loading...</option>}
          </select>

          <select
            value={selectedState}
            onChange={(e) => {
              setSelectedState(e.target.value);
              const dists = Object.keys(locations[selectedCountry][e.target.value]);
              setSelectedDistrict(dists[0]);
              const cities = Object.keys(locations[selectedCountry][e.target.value][dists[0]]);
              setSelectedCity(cities[0]);
            }}
            className="bg-slate-900 border border-slate-800 text-[11px] rounded p-1.5 focus:outline-none focus:border-cyber-cyan text-slate-300 font-semibold cursor-pointer"
          >
            {locations && locations[selectedCountry] ? Object.keys(locations[selectedCountry]).map(s => <option key={s} value={s}>{s}</option>) : <option>Loading...</option>}
          </select>

          <select
            value={selectedDistrict}
            onChange={(e) => {
              setSelectedDistrict(e.target.value);
              const cities = Object.keys(locations[selectedCountry][selectedState][e.target.value]);
              setSelectedCity(cities[0]);
            }}
            className="bg-slate-900 border border-slate-800 text-[11px] rounded p-1.5 focus:outline-none focus:border-cyber-cyan text-slate-300 font-semibold cursor-pointer col-span-2"
          >
            {locations && locations[selectedCountry]?.[selectedState] ? Object.keys(locations[selectedCountry][selectedState]).map(d => <option key={d} value={d}>{d}</option>) : <option>Loading...</option>}
          </select>

          <select
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-[11px] rounded p-1.5 focus:outline-none focus:border-cyber-cyan text-slate-300 font-semibold cursor-pointer col-span-2"
          >
            {locations && locations[selectedCountry]?.[selectedState]?.[selectedDistrict] ? Object.keys(locations[selectedCountry][selectedState][selectedDistrict]).map(c => <option key={c} value={c}>{c}</option>) : <option>Loading...</option>}
          </select>
        </div>
      </div>

      {/* 2. Algorithm Selector & Optimization */}
      <div className="grid grid-cols-2 gap-3 mb-2">
        <div className="col-span-2">
          <label className="text-[9px] uppercase font-bold text-slate-500 tracking-wider block mb-1">Search Logic</label>
          <div className="w-full bg-slate-900 border border-slate-800 text-[11px] rounded p-1.5 text-cyber-cyan font-bold flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <Cpu className="h-3.5 w-3.5" />
              {formatAlgorithmName(activeAlgorithm)}
            </div>
            <div className="text-[9px] text-slate-400 font-normal italic border-t border-slate-800 pt-1 mt-0.5">
              Reason: {getAlgorithmReasoning(activeAlgorithm)}
            </div>
          </div>
        </div>

        <div className="col-span-2">
          <label className="text-[9px] uppercase font-bold text-slate-500 tracking-wider block mb-1">Optim. Target</label>
          <select
            value={optimizationMode}
            onChange={(e) => onOptimizationChange(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 text-[11px] rounded p-1.5 focus:outline-none focus:border-cyber-cyan text-slate-300 font-semibold cursor-pointer"
          >
            <option value="Safe">Safe Mode (Avoid Risk)</option>
            <option value="Eco">Eco Mode (Tailwind Assist)</option>
            <option value="Fast">Fast Mode (Short Distance)</option>
          </select>
        </div>
      </div>

      {/* 3. Obstacle Placer Palette */}
      <div>
        <label className="text-[10px] uppercase font-bold text-slate-500 flex items-center gap-1.5 tracking-widest mb-1.5">
          <AlertOctagon className="h-3.5 w-3.5 text-cyber-red" /> OBSTACLE EDITOR TOOL
        </label>
        <select
          value={obstacleType}
          onChange={(e) => onObstacleTypeChange(e.target.value)}
          className={`w-full bg-slate-900 border text-[11px] rounded p-2 focus:outline-none font-semibold cursor-pointer transition-all ${getObstacleColor(obstacleType)}`}
        >
          <option value="No-Fly Zones">No-Fly Zone (Blocker - Extreme Cost)</option>
          <option value="Skyscrapers">Skyscraper (Build Threat - High Cost)</option>
          <option value="Mountains">Mountain (Elevation Rise - High Cost)</option>
          <option value="Storm Zones">Storm Zone (Turbulence - High Cost)</option>
          <option value="Electric Towers">Electric Tower (Wire Hazard - Med Cost)</option>
          <option value="Bird Flocks">Bird Flock (Dynamic Collide - Med Cost)</option>
          <option value="Other Drones">Other Drone (Separation Breach - Med Cost)</option>
          <option value="Aircraft">Aircraft (High Hazard - Med Cost)</option>
          <option value="Communication Blackout Zones">Comm Blackout (No Telemetry - Low Cost)</option>
          <option value="Trees">Trees (Low Altitude - Low Cost)</option>
        </select>
        <span className="text-[8px] mono-font text-slate-500 mt-1 block">
          * Select type above, then click anywhere on the grid map to instantiate an obstacle.
        </span>
      </div>

      {/* 4. Weather Simulation Presets */}
      <div>
        <label className="text-[10px] uppercase font-bold text-slate-500 flex items-center gap-1.5 tracking-widest mb-1.5">
          <CloudSun className="h-3.5 w-3.5 text-cyber-amber" /> ATMOSPHERIC WEATHER SIMULATOR
        </label>
        <div className="grid grid-cols-5 gap-1 mb-2">
          {['clear', 'rain', 'wind', 'fog', 'storm'].map((cond) => (
            <button
              key={cond}
              onClick={() => handleWeatherConditionChange(cond)}
              className={`text-[9px] font-bold py-1.5 rounded border uppercase transition-all tracking-wider ${
                weather.condition === cond
                  ? 'bg-cyber-amber/15 border-cyber-amber text-cyber-amber shadow-[0_0_8px_rgba(245,158,11,0.25)]'
                  : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              {cond}
            </button>
          ))}
        </div>

        {/* Dynamic sliders if Wind/Storm */}
        {(weather.condition === 'wind' || weather.condition === 'storm' || weather.condition === 'rain') && (
          <div className="bg-slate-950/40 p-2.5 rounded border border-slate-900 grid grid-cols-2 gap-3 mt-2 text-[10px] mono-font text-slate-400">
            <div>
              <div className="flex justify-between mb-0.5">
                <span>WIND VELOCITY</span>
                <span className="text-cyber-amber">{weather.wind_speed} km/h</span>
              </div>
              <input
                type="range"
                min="0"
                max="60"
                value={weather.wind_speed}
                onChange={(e) => onWeatherChange({ ...weather, wind_speed: Number(e.target.value) })}
                className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyber-amber"
              />
            </div>
            <div>
              <div className="flex justify-between mb-0.5">
                <span>WIND BEARING</span>
                <span className="text-cyber-amber flex items-center gap-0.5">
                  <Compass className="h-3 w-3 inline" /> {weather.wind_direction}°
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="360"
                value={weather.wind_direction}
                onChange={(e) => onWeatherChange({ ...weather, wind_direction: Number(e.target.value) })}
                className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyber-amber"
              />
            </div>
          </div>
        )}
      </div>

      {/* 5. Trigger Commands */}
      <div className="flex flex-col gap-2 mt-2 pt-2 border-t border-slate-850">
        <button
          onClick={onPlanRoute}
          disabled={isRunning}
          className="w-full bg-cyber-cyan hover:bg-cyan-500 disabled:opacity-40 text-slate-950 font-bold py-2 rounded text-xs tracking-widest flex items-center justify-center gap-1.5 uppercase transition-all hover:shadow-neon-cyan"
        >
          <Eye className="h-4 w-4" /> Compute Trajectory Plan
        </button>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onStartMission}
            disabled={!hasPath || isRunning}
            className="bg-cyber-green hover:bg-emerald-500 disabled:opacity-40 text-slate-950 font-bold py-1.5 rounded text-[10px] tracking-wider flex items-center justify-center gap-1 uppercase transition-all hover:shadow-neon-green"
          >
            <Play className="h-3.5 w-3.5 fill-slate-950" /> Start Mission
          </button>
          
          <button
            onClick={onExportPdf}
            disabled={!hasPath || isRunning}
            className="bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 font-bold py-1.5 rounded text-[10px] tracking-wider flex items-center justify-center gap-1 uppercase transition-all"
          >
            <FileText className="h-3.5 w-3.5" /> Export PDF Log
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onClearObstacles}
            className="bg-slate-900/60 border border-slate-900 hover:border-slate-800 text-[10px] text-slate-400 py-1 rounded tracking-wider flex items-center justify-center gap-1 transition-all"
          >
            <RotateCcw className="h-3 w-3" /> Clear Obstacles
          </button>
          <button
            onClick={onResetMap}
            className="bg-slate-900/60 border border-slate-900 hover:border-slate-800 text-[10px] text-slate-400 py-1 rounded tracking-wider flex items-center justify-center gap-1 transition-all"
          >
            <RotateCcw className="h-3 w-3" /> Full System Reset
          </button>
        </div>
      </div>
    </div>
  );
}
