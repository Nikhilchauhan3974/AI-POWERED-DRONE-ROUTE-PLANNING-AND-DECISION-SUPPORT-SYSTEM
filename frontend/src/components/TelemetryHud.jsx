import React, { useState } from 'react';
import { Gauge, ArrowUp, Battery, Navigation, Shield, Timer, HelpCircle, Activity, Route, AlertTriangle, Cpu, Zap, Leaf, Rocket } from 'lucide-react';

const ALGO_DESCRIPTIONS = {
  ASTAR: {
    name: "A* Search",
    desc: "Optimal weighted search combining path cost g(n) + heuristic h(n). Guarantees shortest weighted path.",
    icon: <Cpu className="h-4 w-4" />,
    color: "text-cyber-cyan",
    bgColor: "bg-cyber-cyan/10 border-cyber-cyan/20"
  },
  IDASTAR: {
    name: "IDA* Search",
    desc: "Memory-bounded iterative deepening A*. Guarantees shortest weighted path with constant memory.",
    icon: <Cpu className="h-4 w-4" />,
    color: "text-amber-400",
    bgColor: "bg-amber-500/10 border-amber-500/20"
  },
  EXPECTIMAX: {
    name: "Expectimax Search",
    desc: "Adversarial evasion. Evaluates probabilistic outcomes of dynamic obstacles to minimize risk.",
    icon: <Cpu className="h-4 w-4" />,
    color: "text-rose-500",
    bgColor: "bg-rose-500/10 border-rose-500/20"
  },
  HYBRID: {
    name: "Hybrid AI",
    desc: "Ultimate CO6 agent. Uses HMM tracking, Expectimax local evasion, and IDA* global routing.",
    icon: <Rocket className="h-4 w-4" />,
    color: "text-fuchsia-500",
    bgColor: "bg-fuchsia-500/10 border-fuchsia-500/20"
  },
  UCS: {
    name: "Uniform Cost Search",
    desc: "Dijkstra's algorithm — expands lowest cumulative cost g(n), no heuristic. Guarantees minimum-cost path.",
    icon: <Route className="h-4 w-4" />,
    color: "text-violet-400",
    bgColor: "bg-violet-500/10 border-violet-500/20"
  },
  BFS: {
    name: "Breadth-First Search",
    desc: "Unweighted level-by-level expansion. Finds shortest hop-count path but ignores edge costs.",
    icon: <Activity className="h-4 w-4" />,
    color: "text-blue-400",
    bgColor: "bg-blue-500/10 border-blue-500/20"
  },
  DFS: {
    name: "Depth-First Search",
    desc: "Dives deep along one branch before backtracking. Finds ANY path but NOT necessarily the shortest.",
    icon: <Navigation className="h-4 w-4" />,
    color: "text-orange-400",
    bgColor: "bg-orange-500/10 border-orange-500/20"
  },
  GBFS: {
    name: "Greedy Best-First",
    desc: "Expands purely by heuristic h(n) — fastest to goal but may miss optimal path. No cost tracking.",
    icon: <Zap className="h-4 w-4" />,
    color: "text-amber-400",
    bgColor: "bg-amber-500/10 border-amber-500/20"
  }
};

const MODE_INFO = {
  Safe: {
    name: "SAFE MODE",
    desc: "Heavily penalises risky cells (80x risk weight). Path bends widely around obstacles.",
    icon: <Shield className="h-3.5 w-3.5" />,
    color: "text-cyber-green",
    bgColor: "bg-cyber-green/10 border-cyber-green/30"
  },
  Eco: {
    name: "ECO MODE",
    desc: "Leverages wind vectors — reduces cost for tailwind, increases for headwind. Saves battery.",
    icon: <Leaf className="h-3.5 w-3.5" />,
    color: "text-emerald-400",
    bgColor: "bg-emerald-500/10 border-emerald-500/30"
  },
  Fast: {
    name: "FAST MODE",
    desc: "Minimises raw distance. Largely ignores risk — only avoids impassable No-Fly Zones.",
    icon: <Rocket className="h-3.5 w-3.5" />,
    color: "text-red-400",
    bgColor: "bg-red-500/10 border-red-500/30"
  }
};

export default function TelemetryHud({ telemetry, currentCoords, isRunning, algorithmInfo, obstaclesEncountered, totalDistance }) {
  const { speed, altitude, battery_percentage, distance, nodes_visited, execution_time_ms, cost, risk_score } = telemetry;
  const [activeTab, setActiveTab] = useState('telemetry'); // 'telemetry' | 'algorithm' | 'obstacles'

  const algo = ALGO_DESCRIPTIONS[algorithmInfo?.algorithm?.toUpperCase()] || ALGO_DESCRIPTIONS.ASTAR;
  const mode = MODE_INFO[algorithmInfo?.mode] || MODE_INFO.Safe;
  const obstacles = obstaclesEncountered || [];

  const getBatteryColor = (percentage) => {
    if (percentage > 50) return 'text-cyber-green border-cyber-green/20';
    if (percentage > 20) return 'text-cyber-amber border-cyber-amber/20';
    return 'text-cyber-red border-cyber-red/20 animate-pulse';
  };
  
  const getRiskColor = (score) => {
    if (score < 0.2) return 'text-cyber-green';
    if (score < 0.5) return 'text-cyber-amber';
    return 'text-cyber-red animate-pulse';
  };

  return (
    <div className="glass-panel p-4 animate-scan border-t-2 border-t-cyber-cyan shadow-[0_0_15px_rgba(6,182,212,0.15)]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-3">
        <h3 className="text-cyber-cyan text-sm font-bold flex items-center gap-2 tracking-widest">
          <Activity className="h-4 w-4 animate-pulse" /> LIVE TELEMETRY
        </h3>
        <span className={`text-[10px] mono-font px-2 py-0.5 rounded border ${isRunning ? 'bg-cyber-cyan/10 border-cyber-cyan text-cyber-cyan animate-pulse' : 'bg-slate-900 border-slate-700 text-slate-400'}`}>
          {isRunning ? 'TX STREAMING' : 'STANDBY'}
        </span>
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1 mb-3 bg-slate-950/60 rounded p-0.5 border border-slate-800/50">
        {[
          { key: 'telemetry', label: 'Metrics', icon: <Gauge className="h-3 w-3" /> },
          { key: 'algorithm', label: 'Process', icon: <Cpu className="h-3 w-3" /> },
          { key: 'obstacles', label: `Obstacles${obstacles.length > 0 ? ` (${obstacles.length})` : ''}`, icon: <AlertTriangle className="h-3 w-3" /> },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 text-[9px] font-bold uppercase tracking-wider py-1.5 rounded flex items-center justify-center gap-1 transition-all ${
              activeTab === tab.key
                ? 'bg-cyber-cyan/15 text-cyber-cyan border border-cyber-cyan/20 shadow-[0_0_8px_rgba(6,182,212,0.15)]'
                : 'text-slate-500 hover:text-slate-300 border border-transparent'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* TOTAL DISTANCE BANNER — always visible */}
      <div className="mb-3 bg-gradient-to-r from-cyber-cyan/10 via-slate-950/60 to-cyber-cyan/10 border border-cyber-cyan/20 rounded-lg p-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-cyber-cyan/15 border border-cyber-cyan/25 text-cyber-cyan">
            <Route className="h-4 w-4" />
          </div>
          <div>
            <div className="text-[8px] text-slate-500 uppercase tracking-widest font-bold">TOTAL DISTANCE (START → END)</div>
            <div className="text-lg font-black mono-font text-slate-100">
              {(totalDistance || distance || 0).toFixed(0)} <span className="text-xs text-cyber-cyan font-semibold">meters</span>
              <span className="text-[10px] text-slate-500 ml-2">
                ({((totalDistance || distance || 0) / 1000).toFixed(2)} km)
              </span>
            </div>
          </div>
        </div>
        <div className={`text-[9px] font-bold px-2 py-1 rounded border ${mode.bgColor} ${mode.color} uppercase tracking-wider flex items-center gap-1`}>
          {mode.icon} {mode.name}
        </div>
      </div>

      {/* TAB: Telemetry Metrics */}
      {activeTab === 'telemetry' && (
        <>
          <div className="grid grid-cols-2 gap-3">
            {/* Speed */}
            <div className="bg-slate-900/40 p-2 rounded border border-slate-800/60 flex items-center gap-3">
              <div className="p-2 rounded bg-cyber-cyan/10 border border-cyber-cyan/20 text-cyber-cyan">
                <Gauge className="h-4 w-4" />
              </div>
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-wider">Velocity</div>
                <div className="text-sm font-bold mono-font text-slate-100">{speed.toFixed(1)} <span className="text-[10px] text-cyber-cyan">km/h</span></div>
              </div>
            </div>

            {/* Altitude */}
            <div className="bg-slate-900/40 p-2 rounded border border-slate-800/60 flex items-center gap-3">
              <div className="p-2 rounded bg-cyber-cyan/10 border border-cyber-cyan/20 text-cyber-cyan">
                <ArrowUp className="h-4 w-4" />
              </div>
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-wider">Altitude</div>
                <div className="text-sm font-bold mono-font text-slate-100">{altitude.toFixed(0)} <span className="text-[10px] text-cyber-cyan">m</span></div>
              </div>
            </div>

            {/* Battery */}
            <div className="bg-slate-900/40 p-2 rounded border border-slate-800/60 flex items-center gap-3">
              <div className={`p-2 rounded bg-slate-950 border ${getBatteryColor(battery_percentage)}`}>
                <Battery className="h-4 w-4" />
              </div>
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-wider">Battery</div>
                <div className={`text-sm font-bold mono-font ${getBatteryColor(battery_percentage).split(' ')[0]}`}>
                  {battery_percentage.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Distance */}
            <div className="bg-slate-900/40 p-2 rounded border border-slate-800/60 flex items-center gap-3">
              <div className="p-2 rounded bg-cyber-cyan/10 border border-cyber-cyan/20 text-cyber-cyan">
                <Navigation className="h-4 w-4" />
              </div>
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-wider">Range</div>
                <div className="text-sm font-bold mono-font text-slate-100">{(distance).toFixed(0)} <span className="text-[10px] text-cyber-cyan">m</span></div>
              </div>
            </div>

            {/* Nodes Visited */}
            <div className="bg-slate-900/40 p-2 rounded border border-slate-800/60 flex items-center gap-3">
              <div className="p-2 rounded bg-cyber-cyan/10 border border-cyber-cyan/20 text-cyber-cyan">
                <HelpCircle className="h-4 w-4" />
              </div>
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-wider">Scans</div>
                <div className="text-sm font-bold mono-font text-slate-100">{nodes_visited} <span className="text-[10px] text-slate-500">nodes</span></div>
              </div>
            </div>

            {/* Execution Time */}
            <div className="bg-slate-900/40 p-2 rounded border border-slate-800/60 flex items-center gap-3">
              <div className="p-2 rounded bg-cyber-cyan/10 border border-cyber-cyan/20 text-cyber-cyan">
                <Timer className="h-4 w-4" />
              </div>
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-wider">Solver Time</div>
                <div className="text-sm font-bold mono-font text-slate-100">{execution_time_ms.toFixed(2)} <span className="text-[10px] text-cyber-cyan">ms</span></div>
              </div>
            </div>
          </div>

          {/* Grid Coordinates HUD footer */}
          <div className="mt-3 pt-3 border-t border-slate-800/60 grid grid-cols-2 gap-2 text-[10px] mono-font text-slate-400">
            <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/50 flex flex-col">
              <span className="text-slate-500 uppercase tracking-widest text-[8px] mb-0.5">Latitude Target</span>
              <span className="text-slate-200">{currentCoords ? currentCoords.lat.toFixed(6) : "STANDBY"}</span>
            </div>
            <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/50 flex flex-col">
              <span className="text-slate-500 uppercase tracking-widest text-[8px] mb-0.5">Longitude Target</span>
              <span className="text-slate-200">{currentCoords ? currentCoords.lon.toFixed(6) : "STANDBY"}</span>
            </div>
            <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/50 flex flex-col">
              <span className="text-slate-500 uppercase tracking-widest text-[8px] mb-0.5">Traversal Cost</span>
              <span className="text-slate-200">{cost.toFixed(1)}</span>
            </div>
            <div className="bg-slate-950/80 p-1.5 rounded border border-slate-800/50 flex flex-col">
              <span className="text-slate-500 uppercase tracking-widest text-[8px] mb-0.5">Risk Rating</span>
              <span className={`font-semibold uppercase ${getRiskColor(risk_score)}`}>
                {risk_score > 0.6 ? "CRITICAL" : risk_score > 0.2 ? "CAUTION" : "NOMINAL"}
              </span>
            </div>
          </div>
        </>
      )}

      {/* TAB: Algorithm Process Info */}
      {activeTab === 'algorithm' && (
        <div className="flex flex-col gap-3">
          {/* Algorithm Card */}
          <div className={`p-3 rounded-lg border ${algo.bgColor} flex flex-col gap-2`}>
            <div className="flex items-center gap-2">
              <div className={`p-2 rounded ${algo.bgColor} ${algo.color}`}>
                {algo.icon}
              </div>
              <div>
                <div className={`text-sm font-bold ${algo.color} tracking-wider`}>{algo.name}</div>
                <div className="text-[9px] text-slate-400 uppercase tracking-wider">ACTIVE SEARCH ALGORITHM</div>
              </div>
            </div>
            <p className="text-[10px] text-slate-300 leading-relaxed">{algo.desc}</p>
          </div>

          {/* Mode Card */}
          <div className={`p-3 rounded-lg border ${mode.bgColor} flex flex-col gap-2`}>
            <div className="flex items-center gap-2">
              <div className={`p-1.5 rounded ${mode.bgColor} ${mode.color}`}>
                {mode.icon}
              </div>
              <div>
                <div className={`text-xs font-bold ${mode.color} tracking-wider`}>{mode.name}</div>
                <div className="text-[9px] text-slate-400 uppercase tracking-wider">OPTIMIZATION TARGET</div>
              </div>
            </div>
            <p className="text-[10px] text-slate-300 leading-relaxed">{mode.desc}</p>
          </div>

          {/* Stats Summary */}
          <div className="bg-slate-950/60 rounded border border-slate-800/50 p-2.5 grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-[8px] text-slate-500 uppercase tracking-widest">Nodes</div>
              <div className="text-sm font-bold mono-font text-slate-100">{nodes_visited}</div>
            </div>
            <div>
              <div className="text-[8px] text-slate-500 uppercase tracking-widest">Cost</div>
              <div className="text-sm font-bold mono-font text-slate-100">{cost.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-[8px] text-slate-500 uppercase tracking-widest">Time</div>
              <div className="text-sm font-bold mono-font text-slate-100">{execution_time_ms.toFixed(1)}ms</div>
            </div>
          </div>

          {/* Behaviour note for unweighted algorithms */}
          {(algorithmInfo?.algorithm?.toUpperCase() === 'BFS' || algorithmInfo?.algorithm?.toUpperCase() === 'DFS') && (
            <div className="bg-amber-500/5 border border-amber-500/20 rounded p-2 text-[9px] text-amber-400 leading-relaxed flex items-start gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
              <span><strong>Note:</strong> {algorithmInfo.algorithm.toUpperCase()} is an unweighted algorithm. The optimization mode ({algorithmInfo.mode}) is passed to the backend but does NOT change how {algorithmInfo.algorithm.toUpperCase()} selects neighbors — it always uses equal-weight steps. Only A*, UCS, and weighted algorithms respond to mode changes.</span>
            </div>
          )}
        </div>
      )}

      {/* TAB: Obstacles Encountered */}
      {activeTab === 'obstacles' && (
        <div className="flex flex-col gap-2">
          {obstacles.length === 0 ? (
            <div className="bg-slate-950/40 border border-slate-800/50 rounded p-4 text-center text-[10px] text-slate-500 mono-font">
              <Shield className="h-6 w-6 mx-auto mb-2 text-cyber-green opacity-50" />
              <div className="text-cyber-green font-bold uppercase tracking-wider">ALL CLEAR</div>
              <div className="mt-1">No obstacles encountered on the current flight path.</div>
            </div>
          ) : (
            <>
              <div className="text-[9px] text-slate-500 uppercase tracking-wider font-bold mb-1">
                Obstacles the drone's path passes through or avoids:
              </div>
              {obstacles.map((obs, idx) => {
                const isHighRisk = obs.risk >= 0.7;
                const isMedRisk = obs.risk >= 0.3 && obs.risk < 0.7;
                const riskColor = isHighRisk ? 'border-cyber-red/30 bg-cyber-red/5' : isMedRisk ? 'border-cyber-amber/30 bg-cyber-amber/5' : 'border-slate-800/50 bg-slate-950/40';
                const riskTextColor = isHighRisk ? 'text-cyber-red' : isMedRisk ? 'text-cyber-amber' : 'text-cyber-green';

                return (
                  <div key={idx} className={`border rounded p-2.5 flex items-start gap-2.5 ${riskColor}`}>
                    <div className={`p-1.5 rounded border ${riskColor} ${riskTextColor} shrink-0 mt-0.5`}>
                      <AlertTriangle className="h-3.5 w-3.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`text-[11px] font-bold ${riskTextColor} uppercase tracking-wider`}>{obs.type}</div>
                      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 mt-1 text-[9px] mono-font text-slate-400">
                        <div>Cost: <span className="text-slate-200 font-semibold">{obs.cost >= 999 ? '∞ (BLOCKED)' : obs.cost + 'x'}</span></div>
                        <div>Risk: <span className={`font-semibold ${riskTextColor}`}>{(obs.risk * 100).toFixed(0)}%</span></div>
                        <div>Grid: <span className="text-slate-200">({obs.grid_x}, {obs.grid_y})</span></div>
                        <div>Threat: <span className={`font-semibold uppercase ${riskTextColor}`}>
                          {isHighRisk ? 'HIGH' : isMedRisk ? 'MEDIUM' : 'LOW'}
                        </span></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </>
          )}
        </div>
      )}
    </div>
  );
}
