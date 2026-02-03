import React from 'react';

const TeamfightDetails = ({ teamfight }) => {
  if (!teamfight) return null;

  return (
    <div className="bg-gray-800/90 backdrop-blur-md p-6 rounded-2xl border border-blue-500/30 shadow-2xl animate-in zoom-in-95 duration-200">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-black text-white uppercase tracking-tighter flex items-center">
          <span className={`w-3 h-3 rounded-full mr-3 animate-pulse ${teamfight.won ? 'bg-green-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'}`}></span>
          Teamfight Breakdown [@ {teamfight.start_time}]
        </h3>
        <div className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${teamfight.won ? 'border-green-500/50 text-green-400 bg-green-500/10' : 'border-red-500/50 text-red-400 bg-red-500/10'}`}>
          {teamfight.won ? 'Engagement Won' : 'Engagement Lost'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black mb-1">Duration</p>
          <p className="text-xl font-black text-white">{teamfight.end_time_seconds - teamfight.start_time_seconds}s</p>
        </div>
        <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black mb-1">Outcome</p>
          <p className={`text-xl font-black ${teamfight.won ? 'text-green-400' : 'text-red-400'}`}>
            {teamfight.won ? '+1250 Gold' : '-850 Gold'}
          </p>
        </div>
        <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-700">
          <p className="text-[10px] text-gray-500 uppercase font-black mb-1">Cohesion @ Start</p>
          <p className="text-xl font-black text-blue-400">82%</p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center text-xs text-gray-400 italic bg-black/20 p-3 rounded-lg border border-white/5">
          <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Tactical Analysis: Team maintained high cohesion during the initial engage. Loss was primarily due to vision disadvantage in the river brush.
        </div>
        
        <div className="flex justify-end items-center space-x-4">
          <div className="relative w-32 h-32 bg-gray-900 rounded-xl border border-white/5 overflow-hidden shadow-inner">
            <div className="absolute inset-0 opacity-10 bg-[url('https://ddragon.leagueoflegends.com/cdn/14.1.1/img/map/map11.png')] bg-cover"></div>
            {/* Mock positions for snapshot */}
            <div className="absolute top-1/4 left-1/3 w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_5px_rgba(59,130,246,0.8)]"></div>
            <div className="absolute top-1/3 left-1/2 w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_5px_rgba(59,130,246,0.8)]"></div>
            <div className="absolute top-1/2 left-1/4 w-2 h-2 bg-red-500 rounded-full shadow-[0_0_5px_rgba(239,68,68,0.8)] animate-pulse"></div>
            <div className="absolute bottom-2 right-2 text-[8px] text-gray-600 font-mono">T-Snapshot</div>
          </div>
          <button className="text-[10px] font-black uppercase tracking-widest text-blue-400 hover:text-blue-300 transition-colors flex items-center bg-blue-500/10 px-4 py-2 rounded-lg border border-blue-500/20 hover:border-blue-500/40">
            Expand Tactical Map
            <svg className="w-3 h-3 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeamfightDetails;
