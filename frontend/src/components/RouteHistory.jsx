import React from 'react';
import { History, Cloud, Eye, Award } from 'lucide-react';

export default function RouteHistory({ history, onLoadRoute }) {
  return (
    <div className="glass-panel p-4 border-t-2 border-t-slate-700 shadow-[0_0_15px_rgba(100,116,139,0.15)] flex flex-col justify-between h-[210px]">
      <div>
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-2">
          <h3 className="text-slate-400 text-xs font-bold flex items-center gap-1.5 tracking-widest">
            <History className="h-4 w-4" /> MISSION HISTORIES
          </h3>
          <span className="text-[9px] mono-font text-slate-500 uppercase tracking-widest">DB flight vault</span>
        </div>

        <div className="overflow-y-auto max-h-[140px] pr-1 space-y-1.5 scrollbar-thin">
          {history.length > 0 ? (
            history.map((run, i) => (
              <div
                key={run.id || i}
                onClick={() => onLoadRoute(run)}
                className="bg-slate-900/30 hover:bg-slate-900/80 border border-slate-800/60 hover:border-slate-700 p-2 rounded flex items-center justify-between cursor-pointer transition-all group select-none"
              >
                <div>
                  <div className="text-[10.5px] font-bold text-cyber-cyan tracking-wider truncate max-w-[150px]">
                    {run.name}
                  </div>
                  <div className="text-[8px] mono-font text-slate-500 mt-0.5 flex items-center gap-1.5 uppercase">
                    <span className="font-semibold text-slate-400">{run.algorithm}</span>
                    <span>•</span>
                    <span className="flex items-center gap-0.5 text-cyber-amber">
                      <Cloud className="h-2 w-2" /> {run.weather}
                    </span>
                  </div>
                </div>
                
                <div className="text-right flex items-center gap-2">
                  <div className="text-[10px] mono-font text-slate-300 leading-tight">
                    <div>{run.distance.toFixed(0)}m</div>
                    <div className="text-[8px] text-slate-500">{run.battery_consumed.toFixed(1)}% power</div>
                  </div>
                  <Eye className="h-3.5 w-3.5 text-slate-600 group-hover:text-cyber-cyan transition-colors" />
                </div>
              </div>
            ))
          ) : (
            <div className="text-[10px] mono-font text-slate-600 uppercase tracking-widest text-center py-8 flex flex-col items-center gap-1 select-none">
              <Award className="h-4 w-4 text-slate-700" />
              <span>Vault is empty. Save a plan.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
