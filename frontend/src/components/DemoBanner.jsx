import React from 'react';

const DemoBanner = () => {
  return (
    <div className="border-b border-white/10 bg-gradient-to-b from-slate-950 to-slate-950/60 backdrop-blur supports-[backdrop-filter]:bg-slate-950/50">
      <div className="px-6 py-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="text-lg font-black tracking-tight">Demo Coach Console</div>
          <div className="flex gap-2 flex-wrap">
            <span className="px-2.5 py-1 rounded-full text-xs font-mono border border-cyan-400/20 bg-cyan-400/10 text-cyan-200">
              Offline
            </span>
            <span className="px-2.5 py-1 rounded-full text-xs font-mono border border-sky-400/20 bg-sky-400/10 text-sky-200">
              Deterministic
            </span>
            <span className="px-2.5 py-1 rounded-full text-xs font-mono border border-emerald-400/20 bg-emerald-400/10 text-emerald-200">
              Verified
            </span>
          </div>
        </div>

        <div className="text-sm text-slate-300 flex gap-3 flex-wrap items-center">
          <div className="font-mono text-xs px-2.5 py-1 rounded border border-white/10 bg-white/5">
            Dataset scope: Demo pack = 6 matches, baselines computed within pack
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoBanner;
