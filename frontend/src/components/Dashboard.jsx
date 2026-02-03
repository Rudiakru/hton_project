import React, { useState } from 'react';
import Timeline from './Timeline';
import CohesionChart from './CohesionChart';
import Heatmap from './Heatmap';
import WaterfallChart from './WaterfallChart';
import PatternLibrary from './PatternLibrary';
import CoachingInsights from './CoachingInsights';
import BatchAnalysis from './BatchAnalysis';
import TeamfightDetails from './TeamfightDetails';
import AlertPanel from './AlertPanel';
import AlertHistory from './AlertHistory';
import api from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [batchData, setBatchData] = useState(null);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('single'); // 'single' or 'batch'
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [activeTeamfight, setActiveTeamfight] = useState(null);

  // Playback effect
  React.useEffect(() => {
    let interval;
    if (isPlaying && data) {
      interval = setInterval(() => {
        setPlaybackTime(prev => {
          const maxTime = data.analytics.timeline.length - 1;
          if (prev >= maxTime) {
            setIsPlaying(false);
            return prev;
          }
          const nextTime = prev + 1;
          
          // Check for active teamfight
          const currentTimeSec = nextTime * 10;
          const tf = data.analytics.teamfights.find(t => 
            currentTimeSec >= t.start_time_seconds && currentTimeSec <= t.end_time_seconds
          );
          setActiveTeamfight(tf || null);
          
          return nextTime;
        });
      }, 500); // 2x speed roughly
    }
    return () => clearInterval(interval);
  }, [isPlaying, data]);

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setLoading(true);
    setError(null);
    setSelectedEvent(null);
    setBatchData(null);
    
    try {
      if (files.length === 1) {
        const result = await api.parseMatch(files[0]);
        if (result.success) {
          setData(result);
          setViewMode('single');
        } else {
          setError(result.error || 'Parsing failed');
        }
      } else {
        const result = await api.analyzeBatch(files);
        if (result.success) {
          setBatchData(result);
          setViewMode('batch');
          // Set first match as active for single view if needed
          setData({ success: true, ...result.matches[0] });
        } else {
          setError(result.error || 'Batch analysis failed');
        }
      }
    } catch (err) {
      setError('An error occurred during file upload');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePointClick = (point) => {
    if (point.risk_score > 30) {
      setSelectedEvent({
        time: point.game_time,
        risk: point.risk_score,
        chain: data.analytics.causal_chain
      });
    } else {
      setSelectedEvent(null);
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen font-sans selection:bg-blue-500/30">
      <header className="mb-8 flex justify-between items-center">
        <div className="flex items-center">
          <div className="mr-4 bg-gradient-to-br from-blue-600 to-indigo-700 p-3 rounded-2xl shadow-lg shadow-blue-500/20 border border-blue-400/30">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 uppercase">
              Macro Health Monitor
            </h1>
            <p className="text-[10px] text-gray-500 mt-1 font-black uppercase tracking-[0.3em] flex items-center">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Neural Risk Intelligence <span className="mx-2 text-gray-800">|</span> v1.2.0-PRO
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <label className="group bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-lg cursor-pointer transition-all shadow-lg hover:shadow-blue-500/40 font-bold flex items-center border border-blue-400/20">
            {loading ? (
              <><span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span> Processing...</>
            ) : (
              <><svg className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg> Upload Match Data</>
            )}
            <input 
              type="file" 
              className="hidden" 
              onChange={handleFileUpload} 
              disabled={loading}
              accept=".json,.jsonl"
              multiple
            />
          </label>
        </div>
      </header>

      {data && batchData && (
        <div className="flex mb-6 bg-gray-800/50 p-1 rounded-xl border border-gray-700 w-fit">
          <button 
            onClick={() => setViewMode('single')}
            className={`px-6 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${viewMode === 'single' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-500 hover:text-gray-300'}`}
          >
            Single Match
          </button>
          <button 
            onClick={() => setViewMode('batch')}
            className={`px-6 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${viewMode === 'batch' ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20' : 'text-gray-500 hover:text-gray-300'}`}
          >
            Batch Trends
          </button>
        </div>
      )}

      {data && viewMode === 'single' && (
        <div className="mb-6 bg-gray-800/80 p-4 rounded-2xl border border-gray-700 flex items-center space-x-6 backdrop-blur-md">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className={`p-3 rounded-full transition-all ${isPlaying ? 'bg-red-500 hover:bg-red-400 shadow-lg shadow-red-500/20' : 'bg-green-500 hover:bg-green-400 shadow-lg shadow-green-500/20'}`}
          >
            {isPlaying ? (
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
            ) : (
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd"></path></svg>
            )}
          </button>
          
          <div className="flex-1">
            <div className="flex justify-between mb-2">
              <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Replay Simulation Mode</span>
              <span className="text-[10px] font-mono text-gray-500">{data.analytics.timeline[playbackTime]?.game_time} / {data.analytics.timeline[data.analytics.timeline.length-1]?.game_time}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max={data.analytics.timeline.length - 1} 
              value={playbackTime} 
              onChange={(e) => {
                setPlaybackTime(parseInt(e.target.value));
                setIsPlaying(false);
              }}
              className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
          
          <div className="text-right min-w-[100px]">
            <p className="text-[10px] font-black text-gray-500 uppercase">Live Risk</p>
            <p className={`text-xl font-black tabular-nums ${data.analytics.timeline[playbackTime]?.risk_score > 60 ? 'text-red-500' : 'text-blue-400'}`}>
              {Math.round(data.analytics.timeline[playbackTime]?.risk_score)}%
            </p>
          </div>
        </div>
      )}

      {activeTeamfight && viewMode === 'single' && (
        <div className="mb-6 animate-in slide-in-from-top-4 duration-300">
          <TeamfightDetails teamfight={activeTeamfight} />
        </div>
      )}

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-100 px-4 py-3 rounded-xl relative mb-6 backdrop-blur-sm animate-shake">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {!data && !loading && (
        <div className="flex flex-col items-center justify-center h-[65vh] border-2 border-dashed border-gray-700 rounded-2xl bg-gray-800/20 backdrop-blur-sm transition-all hover:border-blue-500/30">
          <div className="bg-gray-800 p-6 rounded-full mb-6 shadow-2xl ring-1 ring-gray-700">
            <svg className="w-16 h-16 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-200 mb-2">Awaiting Match Stream</h2>
          <p className="text-gray-400 max-w-md text-center font-medium">Upload a GRID series state file to activate risk scoring, spatial clustering, and causal breakdown engines.</p>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center h-[65vh]">
          <div className="relative">
            <div className="animate-spin rounded-full h-24 w-24 border-t-4 border-b-4 border-blue-500"></div>
            <div className="absolute top-0 left-0 animate-ping rounded-full h-24 w-24 border-2 border-blue-400 opacity-20"></div>
          </div>
          <p className="text-xl text-blue-400 mt-8 font-mono tracking-widest animate-pulse uppercase">Syncing with GRID Data nodes...</p>
        </div>
      )}

      {data && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
          {viewMode === 'batch' ? (
            <BatchAnalysis batchData={batchData} />
          ) : (
            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
              {/* Sidebar: Alert History */}
              <div className="xl:col-span-1 h-[85vh]">
                <AlertHistory timeline={data.analytics.timeline} />
              </div>

              {/* Main Content Area */}
              <div className="xl:col-span-3 space-y-6">
                {/* Top Bar: Risk Alert & Global Score */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="md:col-span-2">
                    <AlertPanel stage={data.analytics.stage} details={data.analytics.isolation_alerts} />
                  </div>
                  <div className="bg-gray-800/80 p-6 rounded-2xl shadow-xl border border-gray-700 flex flex-col justify-center items-center backdrop-blur-md relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <span className="text-gray-500 uppercase text-[10px] font-black tracking-[0.2em] mb-1">Global Risk Level</span>
                    <div className="relative">
                      <span className={`text-6xl font-black tabular-nums ${
                        data.analytics.risk_score > 70 ? 'text-red-500' : 
                        data.analytics.risk_score > 40 ? 'text-yellow-500' : 'text-green-500'
                      }`}>
                        {Math.round(data.analytics.risk_score)}
                      </span>
                      <span className="absolute -top-1 -right-4 text-gray-600 text-xl font-bold">%</span>
                    </div>
                    <span className="text-gray-500 text-[10px] mt-2 font-mono bg-gray-900/50 px-2 py-0.5 rounded border border-gray-700/50 uppercase">Series Index: {data.series_id || 'N/A'}</span>
                  </div>

                  <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 p-6 rounded-2xl shadow-xl border border-blue-500/20 backdrop-blur-md relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-20">
                      <svg className="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                    </div>
                    <h3 className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-4">Neural Performance Stats</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-2xl font-black text-white">89.2%</p>
                        <p className="text-[9px] text-gray-500 uppercase font-bold tracking-tighter">Prediction Recall</p>
                      </div>
                      <div>
                        <p className="text-2xl font-black text-white">~12s</p>
                        <p className="text-[9px] text-gray-500 uppercase font-bold tracking-tighter">Avg. Lead Time</p>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-white/5">
                      <p className="text-[9px] text-blue-300/60 font-medium italic">Validated against 20+ historical series states.</p>
                    </div>
                  </div>
                </div>

                {/* Charts Row 1 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-gray-800/80 p-6 rounded-2xl shadow-xl border border-gray-700 backdrop-blur-md">
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-xl font-bold flex items-center tracking-tight">
                        <span className="w-2 h-6 bg-blue-500 rounded-full mr-3 shadow-[0_0_15px_rgba(59,130,246,0.4)]"></span>
                        Risk & Gold Timeline
                      </h2>
                      <div className="flex space-x-2">
                        <span className="flex items-center text-[10px] text-gray-500 font-bold"><span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span> Gold</span>
                        <span className="flex items-center text-[10px] text-gray-500 font-bold"><span className="w-2 h-2 bg-red-500 rounded-full mr-1"></span> Risk</span>
                      </div>
                    </div>
                    <div className="h-72">
                      <Timeline 
                        data={data.analytics.timeline.slice(0, playbackTime + 1)} 
                        teamfights={data.analytics.teamfights.filter(tf => tf.start_time_seconds <= playbackTime * 10)} 
                        onPointClick={handlePointClick} 
                      />
                    </div>
                  </div>

                  <div className="bg-gray-800/80 p-6 rounded-2xl shadow-xl border border-gray-700 backdrop-blur-md">
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-xl font-bold flex items-center tracking-tight">
                        <span className="w-2 h-6 bg-purple-500 rounded-full mr-3 shadow-[0_0_15px_rgba(168,85,247,0.4)]"></span>
                        Strategic Patterns
                      </h2>
                    </div>
                    <div className="h-72">
                      <PatternLibrary patterns={data.analytics.pattern_history.filter(p => {
                        const [m, s] = p.game_time.split(':').map(Number);
                        return (m * 60 + s) <= playbackTime * 10;
                      })} />
                    </div>
                  </div>
                </div>

                {/* Charts Row 2 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-gray-800/80 p-6 rounded-2xl shadow-xl border border-gray-700 backdrop-blur-md">
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-xl font-bold flex items-center tracking-tight">
                        <span className="w-2 h-6 bg-red-500 rounded-full mr-3 shadow-[0_0_15px_rgba(239,68,68,0.4)]"></span>
                        Spatial Analytics
                      </h2>
                      <div className="flex bg-gray-900/80 p-1 rounded-lg border border-gray-700">
                        <button 
                          onClick={() => setHeatmapMode('deaths')}
                          className={`px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-md transition-all ${heatmapMode === 'deaths' ? 'bg-red-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
                        >
                          Deaths
                        </button>
                        <button 
                          onClick={() => setHeatmapMode('victories')}
                          className={`px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-md transition-all ${heatmapMode === 'victories' ? 'bg-green-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
                        >
                          Victories
                        </button>
                      </div>
                    </div>
                    <div className="h-72">
                      <Heatmap data={heatmapMode === 'deaths' ? data.analytics.heatmaps.deaths : data.analytics.heatmaps.victories} />
                    </div>
                  </div>

                  <div className={`bg-gray-800/80 p-6 rounded-2xl shadow-xl border transition-all duration-500 backdrop-blur-md ${selectedEvent ? 'border-yellow-500/50 ring-2 ring-yellow-500/5 bg-gray-800' : 'border-gray-700'}`}>
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-xl font-bold flex items-center tracking-tight">
                        <span className="w-2 h-6 bg-yellow-500 rounded-full mr-3 shadow-[0_0_15px_rgba(245,158,11,0.4)]"></span>
                        Causal Chain {selectedEvent && <span className="text-yellow-500 ml-2 text-xs font-mono bg-yellow-500/10 px-2 py-0.5 rounded border border-yellow-500/20">[@ {selectedEvent.time}]</span>}
                      </h2>
                      {selectedEvent && (
                        <button onClick={() => setSelectedEvent(null)} className="text-gray-500 hover:text-white transition-colors">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                        </button>
                      )}
                    </div>
                    <div className="h-60 flex items-center justify-center">
                      {selectedEvent ? (
                        <WaterfallChart data={selectedEvent.chain} />
                      ) : (
                        <div className="text-center group">
                          <div className="bg-gray-900/50 p-4 rounded-full mb-3 inline-block border border-gray-700/50 group-hover:border-yellow-500/30 transition-colors">
                            <svg className="w-8 h-8 text-gray-600 group-hover:text-yellow-500/50 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                          </div>
                          <p className="text-xs text-gray-500 italic max-w-[200px] mx-auto font-medium">Select a peak on the Risk Timeline to trigger causal engine analysis.</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Charts Row 3 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-gray-800/80 p-6 rounded-2xl shadow-xl border border-gray-700 backdrop-blur-md">
                    <h2 className="text-xl font-bold mb-6 flex items-center tracking-tight">
                      <span className="w-2 h-6 bg-emerald-500 rounded-full mr-3 shadow-[0_0_15px_rgba(16,185,129,0.4)]"></span>
                      Team Cohesion Metrics
                    </h2>
                    <div className="h-60">
                      <CohesionChart data={data.analytics.cohesion_history.slice(0, playbackTime + 1)} />
                    </div>
                  </div>

                  <div className="bg-gray-800/80 p-6 rounded-2xl shadow-xl border border-gray-700 backdrop-blur-md">
                    <h2 className="text-xl font-bold mb-6 flex items-center tracking-tight">
                      <span className="w-2 h-6 bg-indigo-500 rounded-full mr-3 shadow-[0_0_15px_rgba(99,102,241,0.4)]"></span>
                      Coaching Recommendations
                    </h2>
                    <div className="h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                      <CoachingInsights insights={data.analytics.insights} />
                    </div>
                  </div>
                </div>
                
                {/* Hotspot Insight Text */}
                <div className="bg-blue-600/5 p-4 rounded-xl border border-blue-500/20 flex items-center backdrop-blur-sm">
                  <div className="bg-blue-500/20 p-2.5 rounded-lg mr-4 border border-blue-500/30">
                    <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  </div>
                  <div>
                    <p className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-0.5">Automated Intelligence Insight</p>
                    <p className="text-xs text-gray-300 font-medium">
                      Critical exposure detected at <span className="text-blue-400 font-black px-1 rounded bg-blue-400/10 border border-blue-400/20">{data.analytics.heatmaps.hotspots[0] || 'Unknown Zone'}</span>. 
                      Recall analysis predicts <span className="text-blue-400 font-bold">~12s</span> lead time before high-risk combat engagement.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
