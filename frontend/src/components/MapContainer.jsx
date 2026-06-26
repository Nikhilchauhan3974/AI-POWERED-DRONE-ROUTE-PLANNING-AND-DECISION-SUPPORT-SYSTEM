import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Play, ShieldAlert, Navigation } from 'lucide-react';

// Re-define Leaflet default icons to avoid asset load bugs
const createStartIcon = () => L.divIcon({
  className: 'custom-start-marker',
  html: `<div class="relative flex items-center justify-center">
           <div class="absolute w-5 h-5 bg-emerald-500 rounded-full opacity-50 animate-ping"></div>
           <div class="w-3.5 h-3.5 bg-emerald-500 border-2 border-white rounded-full shadow-neon-green"></div>
         </div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

const createEndIcon = () => L.divIcon({
  className: 'custom-end-marker',
  html: `<div class="relative flex items-center justify-center">
           <div class="absolute w-5 h-5 bg-red-500 rounded-full opacity-50 animate-ping"></div>
           <div class="w-3.5 h-3.5 bg-red-500 border-2 border-white rounded-full shadow-neon-red"></div>
         </div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

const createDroneIcon = (heading) => L.divIcon({
  className: 'custom-drone-marker',
  html: `<div style="transform: rotate(${heading}deg); transition: transform 0.08s linear;" class="text-cyber-cyan">
           <svg class="h-7 w-7 filter drop-shadow-[0_0_10px_rgba(6,182,212,0.85)]" viewBox="0 0 24 24" fill="currentColor">
             <path d="M12 2C11.45 2 11 2.45 11 3v4.14c-1.39.26-2.58.98-3.41 2.01L5.05 7.61a1 1 0 0 0-1.41 0l-.71.71a1 1 0 0 0 0 1.41l2.54 2.54c-1.03.83-1.75 2.02-2.01 3.41H2a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h1.47c.26 1.39.98 2.58 2.01 3.41l-2.54 2.54a1 1 0 0 0 0 1.41l.71.71a1 1 0 0 0 1.41 0l2.54-2.54c.83 1.03 2.02 1.75 3.41 2.01V22a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1.47c1.39-.26 2.58-.98 3.41-2.01l2.54 2.54a1 1 0 0 0 1.41 0l.71-.71a1 1 0 0 0 0-1.41l-2.54-2.54c1.03-.83 1.75-2.02 2.01-3.41H22a1 1 0 0 0 1-1v-1a1 1 0 0 0-1-1h-1.47c-.26-1.39-.98-2.58-2.01-3.41l2.54-2.54a1 1 0 0 0 0-1.41l-.71-.71a1 1 0 0 0-1.41 0l-2.54 2.54c-.83-1.03-2.02-1.75-3.41-2.01V3a1 1 0 0 0-1-1h-1zm0 7c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 2a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>
           </svg>
         </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});

// Map events handler to capture clicks
function MapEventsHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    }
  });
  return null;
}

// Controller to fly map focus when city changes
function FlyToCenter({ bounds, center }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds([
        [bounds.min_lat, bounds.min_lon],
        [bounds.max_lat, bounds.max_lon]
      ]);
    } else if (center) {
      map.setView([center.lat, center.lon], 14);
    }
  }, [bounds, center, map]);
  return null;
}

export default function MapContainerComponent({
  locationData,
  obstacles,
  onAddObstacle,
  startPoint,
  onSetStartPoint,
  endPoint,
  onSetEndPoint,
  routePath,
  visitedCells,
  isSimulating,
  onSimulationFrame,
  onSimulationFinish,
  obstacleType,
  setCustomTelemetry
}) {
  const [clickMode, setClickMode] = useState('start'); // 'start', 'end', 'obstacle'
  const [animatedVisited, setAnimatedVisited] = useState([]);
  const [visitedProgress, setVisitedProgress] = useState(0);
  const [droneIndex, setDroneIndex] = useState(0);
  const [dronePos, setDronePos] = useState(null);
  const [droneHeading, setDroneHeading] = useState(0);
  const [animatingDrone, setAnimatingDrone] = useState(false);
  
  const timerRef = useRef(null);
  const droneTimerRef = useRef(null);

  const cols = 40;
  const rows = 40;

  // Clear animation states on route change or location reset
  useEffect(() => {
    stopAnimations();
    setAnimatedVisited([]);
    setVisitedProgress(0);
    setDronePos(null);
    setDroneIndex(0);
    setAnimatingDrone(false);
  }, [routePath, locationData]);

  // Animate search exploration when visited cells are updated
  useEffect(() => {
    if (visitedCells && visitedCells.length > 0) {
      stopAnimations();
      setVisitedProgress(0);
      setAnimatedVisited([]);
      
      const stepSize = Math.max(1, Math.floor(visitedCells.length / 80)); // scale speed based on size
      let progress = 0;
      
      timerRef.current = setInterval(() => {
        progress += stepSize;
        if (progress >= visitedCells.length) {
          setAnimatedVisited(visitedCells);
          clearInterval(timerRef.current);
        } else {
          setAnimatedVisited(visitedCells.slice(0, progress));
        }
      }, 10);
    }
    return () => clearInterval(timerRef.current);
  }, [visitedCells]);

  function stopAnimations() {
    if (timerRef.current) clearInterval(timerRef.current);
    if (droneTimerRef.current) clearInterval(droneTimerRef.current);
  };

  // Convert grid coordinates back to GPS lat/lon for visited grid blocks
  const gridCellToLatLon = (x, y) => {
    const { bounds } = locationData;
    const lon = bounds.min_lon + ((x + 0.5) / cols) * (bounds.max_lon - bounds.min_lon);
    const lat = bounds.min_lat + ((y + 0.5) / rows) * (bounds.max_lat - bounds.min_lat);
    return [lat, lon];
  };

  // Convert GPS coordinates to grid cells
  const latLonToGrid = (lat, lon) => {
    const { bounds } = locationData;
    const x = Math.max(0, Math.min(cols - 1, Math.floor(((lon - bounds.min_lon) / (bounds.max_lon - bounds.min_lon)) * cols)));
    const y = Math.max(0, Math.min(rows - 1, Math.floor(((lat - bounds.min_lat) / (bounds.max_lat - bounds.min_lat)) * rows)));
    return [x, y];
  };

  // Calculate heading angle in degrees between two coordinates
  const calculateHeading = (p1, p2) => {
    if (!p1 || !p2) return 0;
    const dy = p2.lat - p1.lat;
    const dx = p2.lon - p1.lon;
    return (Math.atan2(dx, dy) * 180) / Math.PI;
  };

  // Handle map click
  const handleMapClick = (latlng) => {
    if (animatingDrone) return;

    if (clickMode === 'start') {
      onSetStartPoint({ lat: latlng.lat, lon: latlng.lng });
      // Auto toggle to 'end' mode for slick UX
      setClickMode('end');
    } else if (clickMode === 'end') {
      onSetEndPoint({ lat: latlng.lat, lon: latlng.lng });
      setClickMode('obstacle');
    } else if (clickMode === 'obstacle') {
      // Create obstacle with appropriate metadata
      let radius = 150.0;
      let cost = 1.8;
      let risk = 0.3;

      const type = obstacleType;
      if (type.includes('No-Fly')) {
        radius = 220; cost = 999; risk = 1.0;
      } else if (type.includes('Mountain')) {
        radius = 300; cost = 3.5; risk = 0.5;
      } else if (type.includes('Skyscraper')) {
        radius = 120; cost = 4.0; risk = 0.7;
      } else if (type.includes('Storm')) {
        radius = 400; cost = 5.0; risk = 0.8;
      } else if (type.includes('Electric')) {
        radius = 100; cost = 2.0; risk = 0.5;
      } else if (type.includes('Aircraft')) {
        radius = 180; cost = 10.0; risk = 0.9;
      } else if (type.includes('Bird')) {
        radius = 150; cost = 1.8; risk = 0.4;
      } else if (type.includes('Blackout')) {
        radius = 250; cost = 1.5; risk = 0.6;
      } else if (type.includes('Trees')) {
        radius = 110; cost = 1.2; risk = 0.1;
      }

      onAddObstacle({
        type,
        lat: latlng.lat,
        lon: latlng.lng,
        radius,
        risk_level: risk,
        cost
      });
    }
  };

  // Trigger real-time drone animation
  function runDroneFlight() {
    if (!routePath || routePath.length === 0) return;
    
    stopAnimations();
    setAnimatingDrone(true);
    setDroneIndex(0);
    setDronePos(routePath[0]);
    onSimulationFrame(0); // sync backend telemetry index

    let idx = 0;
    droneTimerRef.current = setInterval(() => {
      idx += 1;
      if (idx >= routePath.length) {
        clearInterval(droneTimerRef.current);
        setAnimatingDrone(false);
        onSimulationFinish();
      } else {
        const p1 = routePath[idx - 1];
        const p2 = routePath[idx];
        const heading = calculateHeading(p1, p2);
        
        setDroneIndex(idx);
        setDronePos(p2);
        setDroneHeading(heading);
        onSimulationFrame(idx); // update parent state
      }
    }, 180); // travel speed ticker
  };

  // Bind key trigger to play animation
  useEffect(() => {
    if (isSimulating && !animatingDrone) {
      runDroneFlight();
    }
  }, [isSimulating]);

  // Styling circles for obstacles
  const getObstacleStyle = (type) => {
    const t = type.toLowerCase();
    if (t.includes('no-fly')) return { color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.25, weight: 2.5, dashArray: '4, 4' };
    if (t.includes('storm')) return { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.25, weight: 1.5, dashArray: '10, 5' };
    if (t.includes('mountain')) return { color: '#94a3b8', fillColor: '#475569', fillOpacity: 0.3, weight: 2 };
    if (t.includes('skyscraper')) return { color: '#ec4899', fillColor: '#ec4899', fillOpacity: 0.2, weight: 2 };
    if (t.includes('electric')) return { color: '#eab308', fillColor: '#eab308', fillOpacity: 0.15, weight: 1.5 };
    if (t.includes('blackout')) return { color: '#a855f7', fillColor: '#a855f7', fillOpacity: 0.15, weight: 1.5, dashArray: '1, 5' };
    return { color: '#06b6d4', fillColor: '#06b6d4', fillOpacity: 0.15, weight: 1 };
  };

  // Visited node colors based on algorithms
  const getVisitedNodeColor = () => {
    return 'rgba(6, 182, 212, 0.12)'; // Light cyan
  };

  return (
    <div className="relative w-full h-[580px] rounded-lg overflow-hidden border border-slate-800 shadow-glass dark-map animate-scan">
      {/* HUD Selector Toolbar */}
      <div className="absolute top-3 left-3 z-[1000] flex bg-slate-950/85 border border-slate-800 rounded p-1 shadow-glass backdrop-blur-md text-[10px] uppercase font-bold text-slate-300 gap-1 select-none">
        <button
          onClick={() => setClickMode('start')}
          className={`px-2 py-1 rounded transition-all flex items-center gap-1 ${clickMode === 'start' ? 'bg-cyber-green/15 text-cyber-green border border-cyber-green/20' : 'hover:bg-slate-900 border border-transparent'}`}
        >
          <span className="h-2 w-2 rounded-full bg-cyber-green inline-block"></span> Start
        </button>
        <button
          onClick={() => setClickMode('end')}
          className={`px-2 py-1 rounded transition-all flex items-center gap-1 ${clickMode === 'end' ? 'bg-cyber-red/15 text-cyber-red border border-cyber-red/20' : 'hover:bg-slate-900 border border-transparent'}`}
        >
          <span className="h-2 w-2 rounded-full bg-cyber-red inline-block"></span> Target
        </button>
        <button
          onClick={() => setClickMode('obstacle')}
          className={`px-2 py-1 rounded transition-all flex items-center gap-1 ${clickMode === 'obstacle' ? 'bg-cyber-cyan/15 text-cyber-cyan border border-cyber-cyan/20' : 'hover:bg-slate-900 border border-transparent'}`}
        >
          <span className="h-2 w-2 rounded-full bg-cyber-cyan inline-block animate-pulse"></span> Obstacle
        </button>
      </div>

      {/* Grid Coordinates Display */}
      <div className="absolute bottom-3 right-3 z-[1000] bg-slate-950/80 border border-slate-800 rounded px-2.5 py-1.5 shadow-glass backdrop-blur-sm text-[9px] mono-font text-slate-400 select-none flex flex-col gap-0.5">
        <span className="text-[8px] text-slate-500 uppercase tracking-widest font-semibold">GRID COORDINATE BOUNDS</span>
        <span>LAT RANGE: [{locationData?.bounds.min_lat.toFixed(4)} : {locationData?.bounds.max_lat.toFixed(4)}]</span>
        <span>LON RANGE: [{locationData?.bounds.min_lon.toFixed(4)} : {locationData?.bounds.max_lon.toFixed(4)}]</span>
      </div>

      {/* Main Map Container */}
      {locationData && (
        <MapContainer
          center={[locationData.center.lat, locationData.center.lon]}
          zoom={14}
          style={{ width: '100%', height: '100%', outline: 'none' }}
          className="dark-map"
        >
          {/* CartoDB Dark Matter tile server */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          <FlyToCenter bounds={locationData.bounds} center={locationData.center} />
          <MapEventsHandler onMapClick={handleMapClick} />

          {/* Visited Cells Grid Overlay */}
          {animatedVisited.map(([x, y], idx) => {
            const cellCenter = gridCellToLatLon(x, y);
            const size = 65; // meters width approximately
            return (
              <Circle
                key={`visited-${x}-${y}-${idx}`}
                center={cellCenter}
                radius={size / 2}
                pathOptions={{
                  stroke: false,
                  fillColor: getVisitedNodeColor(),
                  fillOpacity: 0.35
                }}
              />
            );
          })}

          {/* Placed Obstacles */}
          {obstacles.map((obs, idx) => (
            <Circle
              key={`obstacle-${idx}`}
              center={[obs.lat, obs.lon]}
              radius={obs.radius}
              pathOptions={getObstacleStyle(obs.type)}
            >
              <Popup>
                <div className="text-[10px] leading-relaxed mono-font">
                  <div className="font-bold text-cyber-cyan border-b border-slate-850 pb-1 mb-1 uppercase">
                    {obs.type}
                  </div>
                  <div>Cost Multiplier: <span className="font-semibold text-slate-100">{obs.cost}x</span></div>
                  <div>Risk Factor: <span className="font-semibold text-slate-100">{obs.risk_level}</span></div>
                  <div>Buffer Radius: <span className="font-semibold text-slate-100">{obs.radius.toFixed(0)}m</span></div>
                </div>
              </Popup>
            </Circle>
          ))}

          {/* Start Point */}
          {startPoint && (
            <Marker position={[startPoint.lat, startPoint.lon]} icon={createStartIcon()}>
              <Popup>
                <div className="text-[10px] mono-font">
                  <span className="font-bold text-cyber-green">FLIGHT START</span><br />
                  LAT: {startPoint.lat.toFixed(5)}<br />
                  LON: {startPoint.lon.toFixed(5)}
                </div>
              </Popup>
            </Marker>
          )}

          {/* End Point */}
          {endPoint && (
            <Marker position={[endPoint.lat, endPoint.lon]} icon={createEndIcon()}>
              <Popup>
                <div className="text-[10px] mono-font">
                  <span className="font-bold text-cyber-red">FLIGHT TARGET</span><br />
                  LAT: {endPoint.lat.toFixed(5)}<br />
                  LON: {endPoint.lon.toFixed(5)}
                </div>
              </Popup>
            </Marker>
          )}

          {/* Traveled Route Polyline */}
          {routePath && routePath.length > 0 && (
            <Polyline
              positions={routePath.map(p => [p.lat, p.lon])}
              pathOptions={{
                color: '#06b6d4',
                weight: 3.5,
                opacity: 0.85,
                lineCap: 'round',
                lineJoin: 'round',
                dashArray: animatingDrone ? '10, 5' : null,
                className: 'drop-shadow-[0_0_12px_rgba(6,182,212,0.85)]'
              }}
            />
          )}

          {/* Drone Marker */}
          {dronePos && (
            <Marker position={[dronePos.lat, dronePos.lon]} icon={createDroneIcon(droneHeading)}>
              <Popup>
                <div className="text-[9px] leading-relaxed mono-font">
                  <div className="font-bold text-cyber-cyan">AERO-COM QUAD_18</div>
                  <div>STATUS: Traversing Waypoint</div>
                  <div>LAT: {dronePos.lat.toFixed(5)}</div>
                  <div>LON: {dronePos.lon.toFixed(5)}</div>
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      )}
    </div>
  );
}
