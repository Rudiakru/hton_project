import React from 'react';

const AlertHistory = ({ timeline }) => {
  // Filter timeline points where risk score significantly changed or stage transition occurred
  const transitions = [];
  let lastStage = null;

  const getStage = (score) => {
    if (score >= 60) return "WINNING";
    if (score >= 40) return "COMPETITIVE";
    if (score >= 20) return "VULNERABLE";
    return "CRITICAL";
  };

  timeline.forEach((point, index) => {
    const currentStage = getStage(point.risk_score);
    if (lastStage && currentStage !== lastStage) {
      transitions.push({
        time: point.game_time,
        from: lastStage,
        to: currentStage,
        score: point.risk_score
      });
    }
    lastStage = currentStage;
  });

  return (
    <div className="bg-gray-800/50 rounded-2xl border border-gray-700 h-full overflow-hidden flex flex-col">
      <div className="p-4 border-b border-gray-700 bg-gray-800 flex items-center justify-between">
        <h3 className="text-sm font-black uppercase tracking-widest text-gray-400">Macro Alert History</h3>
        <span className="bg-blue-500/20 text-blue-400 text-[10px] px-2 py-0.5 rounded-full font-bold">
          {transitions.length} Events
        </span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {transitions.length === 0 && (
          <p className="text-gray-500 text-xs italic text-center mt-10">No stage transitions detected yet.</p>
        )}
        {[...transitions].reverse().map((t, i) => (
          <div key={i} className="relative pl-4 border-l border-gray-700 py-1">
            <div className={`absolute left-[-5px] top-2 w-2 h-2 rounded-full ${
              t.to === 'CRITICAL' ? 'bg-red-500' : 
              t.to === 'VULNERABLE' ? 'bg-orange-500' : 
              t.to === 'COMPETITIVE' ? 'bg-yellow-500' : 'bg-green-500'
            }`}></div>
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-mono text-gray-500">{t.time}</span>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                t.to === 'CRITICAL' ? 'bg-red-500/10 text-red-500' : 
                t.to === 'VULNERABLE' ? 'bg-orange-500/10 text-orange-500' : 
                t.to === 'COMPETITIVE' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-green-500/10 text-green-500'
              }`}>
                {t.to}
              </span>
            </div>
            <p className="text-xs text-gray-300 mt-1">
              Shift from <span className="text-gray-500">{t.from}</span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlertHistory;
