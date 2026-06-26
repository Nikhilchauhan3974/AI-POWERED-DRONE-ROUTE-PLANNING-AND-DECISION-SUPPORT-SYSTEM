import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { BarChart3, Activity } from 'lucide-react';

export default function ComparisonDashboard({ comparisonData }) {
  const [activeMetric, setActiveMetric] = useState('execution_time_ms');

  const metrics = [
    { id: 'execution_time_ms', label: 'Solve Time (ms)', color: '#06b6d4' },
    { id: 'battery_consumed', label: 'Battery (%)', color: '#f59e0b' },
    { id: 'distance', label: 'Distance (m)', color: '#10b981' },
    { id: 'nodes_visited', label: 'Scanned Nodes', color: '#a855f7' }
  ];

  const currentMetric = metrics.find(m => m.id === activeMetric);

  // Map dataset
  const chartData = comparisonData.map(item => {
    let val = 0;
    if (activeMetric === 'execution_time_ms') val = item.avg_execution_time_ms;
    else if (activeMetric === 'battery_consumed') val = item.avg_battery_consumed;
    else if (activeMetric === 'distance') val = item.avg_path_length * 100.0; // scale cell distance to mock meters or use actual
    else val = item.avg_nodes_visited;

    // Use actual distance if available
    if (activeMetric === 'distance' && item.avg_distance) {
      val = item.avg_distance;
    } else if (activeMetric === 'distance' && !item.avg_distance) {
      // If we only have avg_path_length, map it to meters roughly
      val = item.avg_path_length * 150.0;
    }

    return {
      name: item.algorithm,
      value: Number(val.toFixed(2))
    };
  });

  // Color mappings for specific algorithms
  const ALGO_COLORS = {
    'AStar': '#06b6d4', // Cyan
    'IDAStar': '#f59e0b', // Amber
    'Expectimax': '#f43f5e', // Rose
    'Hybrid': '#d946ef', // Fuchsia
    'UCS': '#eab308',   // Yellow
    'GBFS': '#ef4444',  // Red
    'DFS': '#ef4444'    // Red
  };

  return (
    <div className="glass-panel p-4 border-t-2 border-t-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-3">
        <h3 className="text-purple-400 text-xs font-bold flex items-center gap-1.5 tracking-widest">
          <BarChart3 className="h-4 w-4" /> ALGORITHM BENCHMARKS
        </h3>
        <span className="text-[9px] mono-font text-purple-400 uppercase tracking-widest">Real-time telemetry comparison</span>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1 mb-3">
        {metrics.map(metric => (
          <button
            key={metric.id}
            onClick={() => setActiveMetric(metric.id)}
            className={`text-[9px] font-semibold tracking-wider uppercase px-2 py-1 rounded transition-all border ${
              activeMetric === metric.id
                ? 'bg-purple-950/30 border-purple-500 text-purple-400 shadow-[0_0_8px_rgba(168,85,247,0.25)]'
                : 'bg-slate-900/40 border-slate-800/60 text-slate-400 hover:border-slate-700'
            }`}
          >
            {metric.label.split(' ')[0]}
          </button>
        ))}
      </div>

      {/* Recharts Bar Chart */}
      <div className="h-[130px] w-full bg-slate-950/40 rounded border border-slate-900/60 p-1 flex items-center justify-center">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: -28, bottom: 0 }}>
              <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" vertical={false} />
              <XAxis 
                dataKey="name" 
                stroke="#64748b" 
                fontSize={8} 
                tickLine={false} 
                axisLine={false}
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={8} 
                tickLine={false} 
                axisLine={false}
              />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: 'rgba(15, 23, 42, 0.95)', 
                  borderColor: '#1e293b', 
                  borderRadius: '6px',
                  fontSize: '9px',
                  fontFamily: 'Consolas, monospace',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
                }}
                itemStyle={{ color: '#f8fafc' }}
                cursor={{ fill: 'rgba(148, 163, 184, 0.04)' }}
              />
              <Bar 
                dataKey="value" 
                radius={[3, 3, 0, 0]}
                maxBarSize={22}
              >
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={ALGO_COLORS[entry.name] || currentMetric.color} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-[10px] mono-font text-slate-600 uppercase tracking-widest flex items-center gap-1">
            <Activity className="h-3 w-3 animate-pulse" /> Benchmarking database logs...
          </div>
        )}
      </div>
    </div>
  );
}
