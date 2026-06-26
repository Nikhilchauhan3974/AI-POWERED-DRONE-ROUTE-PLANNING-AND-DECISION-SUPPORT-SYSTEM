import React, { useState, useEffect } from 'react';
import { Terminal, ShieldAlert, Cpu } from 'lucide-react';

export default function AiAdvisor({ recommendation }) {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText('');
    if (!recommendation) {
      setDisplayedText("SYSTEM DIAGNOSTICS: Standing by. Awaiting flight route coordinates configuration...");
      return;
    }

    let index = 0;
    const textToType = recommendation;
    
    const intervalId = setInterval(() => {
      setDisplayedText((prev) => prev + textToType[index]);
      index++;
      if (index >= textToType.length - 1) {
        clearInterval(intervalId);
      }
    }, 12); // Typing animation speed

    return () => clearInterval(intervalId);
  }, [recommendation]);

  const advices = displayedText.split(' | ');

  return (
    <div className="glass-panel p-4 border-l-2 border-l-cyber-amber shadow-[0_0_15px_rgba(245,158,11,0.15)] flex flex-col justify-between h-[180px]">
      <div>
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-2.5">
          <h3 className="text-cyber-amber text-xs font-bold flex items-center gap-1.5 tracking-widest">
            <Cpu className="h-4 w-4 text-cyber-amber" /> AI ROUTING ADVISOR
          </h3>
          <span className="text-[9px] mono-font text-cyber-amber animate-pulse">ANALYZING GRID</span>
        </div>

        <div className="overflow-y-auto max-h-[110px] pr-1 space-y-2 text-[10.5px] leading-relaxed mono-font scrollbar-thin">
          {advices.map((advice, i) => {
            if (!advice.trim()) return null;
            
            const isAlarm = 
              advice.startsWith('CRITICAL') || 
              advice.startsWith('BATTERY') || 
              advice.startsWith('HAZARD') || 
              advice.includes('WARNING');
              
            return (
              <div 
                key={i} 
                className={`flex items-start gap-1.5 p-1 rounded ${
                  isAlarm 
                    ? 'bg-cyber-red/10 border border-cyber-red/20 text-cyber-red' 
                    : 'text-slate-300'
                }`}
              >
                {isAlarm && (
                  <ShieldAlert className="h-3 w-3 mt-0.5 shrink-0 text-cyber-red animate-pulse" />
                )}
                <span>{advice}</span>
              </div>
            );
          })}
        </div>
      </div>
      <div className="text-[8px] mono-font text-slate-600 text-right uppercase tracking-widest mt-1">
        Expert Core v9.42 // Offline Mode
      </div>
    </div>
  );
}
