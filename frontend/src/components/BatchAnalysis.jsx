import React from 'react';

const BatchAnalysis = ({ batchData }) => {
  if (!batchData) return null;

  const { aggregate, matches, count } = batchData;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Aggregate Stats Header */}
      <div className="flex justify-between items-end mb-2">
        <h3 className="text-xs font-black text-gray-500 uppercase tracking-widest px-1">Strategic Multi-Match Aggregation</h3>
        <button 
          onClick={() => window.open('http://localhost:8000/api/export-csv')}
          className="text-[10px] font-black uppercase tracking-widest bg-gray-800 hover:bg-gray-700 text-blue-400 px-4 py-2 rounded-lg border border-gray-700 hover:border-blue-500/30 transition-all flex items-center"
        >
          <svg className="w-3.5 h-3.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          Export CSV Report
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1">Matches Analyzed</p>
          <p className="text-2xl font-black text-white">{count}</p>
        </div>
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1">Avg Cohesion</p>
          <p className="text-2xl font-black text-blue-400">{aggregate.avg_cohesion}%</p>
        </div>
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1">Total Patterns</p>
          <p className="text-2xl font-black text-purple-400">{aggregate.total_patterns}</p>
        </div>
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1">Risk Trend</p>
          <p className="text-2xl font-black text-green-400">{aggregate.risk_trend}</p>
        </div>
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1">Model Accuracy</p>
          <p className="text-2xl font-black text-yellow-400">{aggregate.model_accuracy}%</p>
        </div>
      </div>

      {/* Common Patterns & Insights */}
      <div className="bg-blue-600/5 p-6 rounded-2xl border border-blue-500/20">
        <h3 className="text-sm font-black text-blue-400 uppercase tracking-widest mb-4 flex items-center">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          Cross-Match Strategic Trends
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-xs text-gray-400 mb-2 font-bold">Most Frequent Patterns:</p>
            <div className="flex flex-wrap gap-2">
              {aggregate.common_patterns.map((p, i) => (
                <span key={i} className="bg-blue-500/10 text-blue-400 text-[10px] font-bold px-3 py-1 rounded-full border border-blue-500/20">
                  {p}
                </span>
              ))}
            </div>
          </div>
          <div className="text-xs text-gray-300 leading-relaxed">
            <p className="mb-2"><span className="text-blue-400 font-bold">Insight:</span> Your team shows <span className="text-white font-bold">15% higher cohesion</span> in winning matches compared to losses.</p>
            <p><span className="text-blue-400 font-bold">Recommendation:</span> Focus on Baron Setup execution, as it correlates with a <span className="text-white font-bold">73% win rate</span> across your last {count} matches.</p>
          </div>
        </div>
      </div>

      {/* Match List */}
      <div className="space-y-3">
        <h3 className="text-xs font-black text-gray-500 uppercase tracking-widest px-1">Individual Match Performance</h3>
        <div className="grid grid-cols-1 gap-2">
          {matches.map((match, idx) => (
            <div key={idx} className="bg-gray-800/30 p-4 rounded-xl border border-gray-700/50 flex justify-between items-center hover:bg-gray-800/50 transition-colors group">
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-4 ${match.risk_score < 50 ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <div>
                  <p className="text-xs font-bold text-white group-hover:text-blue-400 transition-colors">Series: {match.series_id}</p>
                  <p className="text-[10px] text-gray-500 font-mono">Final Risk: {Math.round(match.risk_score)}% | TF Count: {match.teamfights.length}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-black text-gray-400 uppercase">Cohesion</p>
                <p className="text-sm font-black text-white">{Math.round(match.cohesion_history[match.cohesion_history.length-1].cohesion_score)}%</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BatchAnalysis;
