import React from 'react';

const PatternLibrary = ({ patterns }) => {
  if (!patterns || patterns.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8 bg-gray-900/30 rounded-2xl border border-dashed border-gray-800">
        <div className="bg-gray-800/50 p-3 rounded-full mb-3">
          <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
        </div>
        <p className="text-gray-500 text-sm font-medium italic">No strategic patterns detected yet.</p>
        <p className="text-xs text-gray-600 mt-1">Patterns appear as teams execute recognized macro setups.</p>
      </div>
    );
  }

  // Group patterns to show frequency or latest
  const patternSummary = patterns.reduce((acc, curr) => {
    const p = curr.pattern;
    if (!acc[p.id]) {
      acc[p.id] = { ...p, count: 0, times: [] };
    }
    acc[p.id].count += 1;
    acc[p.id].times.push(curr.game_time);
    return acc;
  }, {});

  return (
    <div className="space-y-3 overflow-y-auto max-h-[350px] pr-2 custom-scrollbar">
      {Object.values(patternSummary).map((pattern) => (
        <div key={pattern.id} className="bg-gray-900/50 p-4 rounded-xl border border-gray-700/50 hover:border-blue-500/40 hover:bg-gray-900/80 transition-all group relative overflow-hidden">
          <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/5 rounded-bl-full -mr-8 -mt-8 group-hover:bg-blue-500/10 transition-colors"></div>
          
          <div className="flex justify-between items-start mb-2 relative z-10">
            <div>
              <h3 className="font-bold text-blue-400 group-hover:text-blue-300 transition-colors flex items-center">
                {pattern.label}
                <span className="ml-2 w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></span>
              </h3>
              <p className="text-[10px] text-gray-500 font-mono uppercase tracking-tighter mt-0.5">Tactical Pattern Signature</p>
            </div>
            <div className="text-right">
              <div className="bg-blue-600/20 text-blue-400 text-[10px] font-black px-2 py-0.5 rounded border border-blue-500/30 inline-block shadow-sm">
                {Math.round(pattern.win_rate * 100)}% Win Rate
              </div>
              <p className="text-[10px] text-gray-500 mt-1 uppercase font-black tracking-widest">Occurrences: {pattern.count}</p>
            </div>
          </div>
          
          <p className="text-xs text-gray-400 mb-4 leading-relaxed relative z-10">{pattern.description}</p>
          
          <div className="flex flex-wrap gap-1.5 relative z-10">
            <span className="text-[9px] text-gray-500 uppercase font-bold mr-1 self-center">Timestamps:</span>
            {pattern.times.slice(-4).map((t, i) => (
              <span key={i} className="text-[9px] bg-gray-800/80 text-blue-300/70 px-2 py-0.5 rounded border border-gray-700 font-mono shadow-inner">
                {t}
              </span>
            ))}
            {pattern.times.length > 4 && (
              <span className="text-[9px] bg-gray-800/40 text-gray-600 px-2 py-0.5 rounded border border-gray-700/50 font-mono">
                +{pattern.times.length - 4} more
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PatternLibrary;
