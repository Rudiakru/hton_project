import React from 'react';

const CoachingInsights = ({ insights }) => {
  if (!insights || insights.length === 0) return null;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'border-red-500/50 bg-red-500/10 text-red-400';
      case 'HIGH': return 'border-orange-500/50 bg-orange-500/10 text-orange-400';
      case 'MEDIUM': return 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400';
      default: return 'border-blue-500/50 bg-blue-500/10 text-blue-400';
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'COHESION': return 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z';
      case 'VISION': return 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z';
      case 'RISK': return 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z';
      default: return 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.364-6.364l-.707-.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M12 3c-4.97 0-9 4.03-9 9 0 4.97 4.03 9 9 9s9-4.03 9-9c0-4.97-4.03-9-9-9z';
    }
  };

  const copyToClipboard = () => {
    const text = insights.map(i => `${i.title}: ${i.recommendation}`).join('\n\n');
    navigator.clipboard.writeText(text);
    alert('Insights copied to clipboard!');
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button 
          onClick={copyToClipboard}
          className="text-[10px] font-black uppercase tracking-widest text-gray-500 hover:text-blue-400 transition-colors flex items-center"
        >
          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h.01M9 12h.01M11 12h5M11 16h5"></path>
          </svg>
          Copy Insights
        </button>
      </div>
      {insights.map((insight, idx) => (
        <div key={idx} className={`p-4 rounded-xl border-2 transition-all ${getSeverityColor(insight.severity)}`}>
          <div className="flex items-start">
            <div className="p-2 rounded-lg bg-gray-900/50 mr-4 mt-1 border border-white/10">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={getIcon(insight.type)}></path>
              </svg>
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <h3 className="font-black uppercase tracking-tighter text-sm">{insight.title}</h3>
                <span className="text-[10px] font-mono opacity-60 uppercase">{insight.severity}</span>
              </div>
              <p className="text-xs font-bold mb-2 text-white/90">Observation: {insight.observation}</p>
              
              <div className="bg-black/20 p-3 rounded-lg border border-white/5 mb-2">
                <p className="text-[10px] uppercase font-black tracking-widest text-white/50 mb-1">Actionable Recommendation</p>
                <p className="text-xs text-white leading-relaxed">{insight.recommendation}</p>
              </div>
              
              <div className="flex items-center text-[10px] font-bold opacity-70 italic">
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                Impact: {insight.impact}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CoachingInsights;
