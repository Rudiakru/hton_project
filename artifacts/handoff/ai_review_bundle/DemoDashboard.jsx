import React, { useEffect, useMemo, useState } from 'react';
import api from '../services/api';
import DemoBanner from './DemoBanner';
import EvidenceDrawer from './EvidenceDrawer';

const DemoDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [matches, setMatches] = useState([]);
  const [teams, setTeams] = useState([]);
  const [matchId, setMatchId] = useState('');
  const [teamId, setTeamId] = useState('');

  const [moments, setMoments] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [integrity, setIntegrity] = useState(null);
  const [observationMasking, setObservationMasking] = useState(null);
  const [benchmarks, setBenchmarks] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [panel, setPanel] = useState(null);

  const [showMethodology, setShowMethodology] = useState(false);

  const HERO_MATCH = 'TL-C9-G2';
  const HERO_TEAM = 'TL';
  const [demoGuideStep, setDemoGuideStep] = useState(0); // 0=idle, 1=moments opened, 2=scout opened

  const formatMmSs = (tsSeconds) => {
    const s = Math.max(0, Number(tsSeconds) || 0);
    const mm = Math.floor(s / 60);
    const ss = Math.floor(s % 60);
    return `${mm}:${String(ss).padStart(2, '0')}`;
  };

  const formatMatchLabel = (mid) => {
    if (!mid || typeof mid !== 'string') return '';
    const parts = mid.split('-');
    if (parts.length < 3) return mid;
    const a = parts[0];
    const b = parts[1];
    const g = parts[2];
    const gameNum = (g && g.toUpperCase().startsWith('G')) ? g.slice(1) : g;
    return `${a} vs ${b} • Game ${gameNum}`;
  };

  const topMoment = moments && moments.length > 0 ? moments[0] : null;
  const topMomentTs = topMoment ? (Number(topMoment.start_ts) + 30) : null;
  const topMomentLabel = (matchId && topMomentTs != null)
    ? `${formatMatchLabel(matchId)} @ ${formatMmSs(topMomentTs)}`
    : '';

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [health, m, t, integ, mask, bench] = await Promise.all([
          api.demoHealth(),
          api.demoMatches(),
          api.demoTeams(),
          api.demoIntegrity(),
          api.demoObservationMasking(),
          api.demoBenchmarks(),
        ]);
        if (!mounted) return;
        setDatasetInfo(health.dataset || null);
        setMatches(m.matches || []);
        setTeams(t.teams || []);
        setIntegrity(integ);
        setObservationMasking(mask);
        setBenchmarks(bench);
        if ((m.matches || []).length > 0) setMatchId(m.matches[0]);
        if ((t.teams || []).length > 0) setTeamId(t.teams[0]);
      } catch (e) {
        const detail = e?.response?.data?.detail;
        if (!e?.response) {
          setError(
            'Backend not reachable. Fix: start the backend in demo mode (set DEMO_PACK_ROOT and run uvicorn), then reload the page.'
          );
        } else if (detail && typeof detail === 'string' && detail.toLowerCase().includes('demo pack corrupted')) {
          setError(`Demo pack corrupted. ${detail}`);
        } else {
          setError('Failed to load demo data');
        }
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, []);

  const selectedMomentEvidenceId = useMemo(() => {
    if (!moments || moments.length === 0) return '';
    return moments[0].primary_event_ref;
  }, [moments]);

  const onShowMoments = async () => {
    if (!matchId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.demoShowMoments(matchId);
      setMoments(res.moments || []);
    } catch (e) {
      setError('Failed to load moments');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const onScoutTeam = async () => {
    if (!teamId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.demoScoutTeam(teamId);
      setPatterns(res.patterns || []);
    } catch (e) {
      setError('Failed to load scouting report');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const openEvidence = async (evidenceId) => {
    if (!evidenceId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.demoAnalyzeMoment(evidenceId);
      setPanel(res.panel);
      setDrawerOpen(true);
    } catch (e) {
      setError('Failed to load evidence panel');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const startDemo = async () => {
    setDemoGuideStep(0);
    setError(null);

    const targetMatch = matches.includes(HERO_MATCH) ? HERO_MATCH : (matches[0] || '');
    const targetTeam = teams.includes(HERO_TEAM) ? HERO_TEAM : (teams[0] || '');
    if (!targetMatch || !targetTeam) return;

    setMatchId(targetMatch);
    setTeamId(targetTeam);

    try {
      setLoading(true);
      const res = await api.demoShowMoments(targetMatch);
      const ms = res.moments || [];
      setMoments(ms);
      if (ms.length > 0) {
        const evidenceId = ms[0].primary_event_ref;
        const panelRes = await api.demoAnalyzeMoment(evidenceId);
        setPanel(panelRes.panel);
        setDrawerOpen(true);
      }
      setDemoGuideStep(1);
    } catch (e) {
      setError('Start Demo failed');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const nextDemoStep = async () => {
    if (demoGuideStep < 1) return;
    setError(null);
    try {
      setLoading(true);
      const res = await api.demoScoutTeam(teamId);
      const ps = res.patterns || [];
      setPatterns(ps);
      if (ps.length > 0 && ps[0].instances && ps[0].instances.length > 0) {
        const evidenceId = ps[0].instances[0].evidence_refs[0];
        const panelRes = await api.demoAnalyzeMoment(evidenceId);
        setPanel(panelRes.panel);
        setDrawerOpen(true);
      }
      setDemoGuideStep(2);
    } catch (e) {
      setError('Next step failed');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <DemoBanner />
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-start gap-6 flex-wrap">
          <div>
            <div className="text-2xl font-black tracking-tight">Demo path</div>
            <div className="text-sm text-slate-300">One obvious route: Start Demo → Next. Every insight is click-to-verify (offline).</div>
            <div className="mt-3 flex gap-2 flex-wrap">
              <button
                data-testid="start-demo"
                className="text-base px-5 py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-xl font-extrabold shadow-lg shadow-cyan-500/10 disabled:opacity-60 disabled:hover:bg-cyan-500"
                onClick={startDemo}
                disabled={loading}
              >
                Start Demo
              </button>
              <button
                data-testid="next-step"
                className="text-base px-5 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-semibold disabled:opacity-50"
                onClick={nextDemoStep}
                disabled={loading || demoGuideStep < 1}
              >
                Next
              </button>
            </div>
            <button
              className="mt-2 text-sm px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg"
              onClick={() => setShowMethodology((v) => !v)}
            >
              {showMethodology ? 'Hide' : 'Show'} coach notes
            </button>
          </div>

          <details className="bg-white/5 border border-white/10 rounded-2xl p-4">
            <summary className="cursor-pointer select-none text-sm opacity-80 hover:opacity-100">Advanced selectors</summary>
            <div className="mt-3 flex gap-4 items-end flex-wrap">
              <div>
                <div className="text-xs opacity-70 mb-1">Match</div>
                <select
                  id="match-selector"
                  className="bg-black/30 border border-white/10 rounded-lg px-3 py-2"
                  value={matchId}
                  onChange={(e) => setMatchId(e.target.value)}
                >
                  {matches.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
              <div>
                <div className="text-xs opacity-70 mb-1">Team</div>
                <select
                  id="team-selector"
                  className="bg-black/30 border border-white/10 rounded-lg px-3 py-2"
                  value={teamId}
                  onChange={(e) => setTeamId(e.target.value)}
                >
                  {teams.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-sky-600 hover:bg-sky-500 rounded-lg" onClick={onShowMoments}>
                  Show moments
                </button>
                <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg" onClick={() => openEvidence(selectedMomentEvidenceId)}>
                  Open top evidence
                </button>
                <button className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg" onClick={onScoutTeam}>
                  Generate report
                </button>
              </div>
            </div>
          </details>
        </div>

        {(demoGuideStep >= 1) && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-xs font-mono opacity-70">What happened</div>
              <div className="mt-1 font-semibold">{topMoment?.title || 'Top moment loaded'}</div>
              <div className="text-sm opacity-80 mt-1">{topMoment?.description || 'Evidence opened for the top moment.'}</div>
              {topMomentLabel && (
                <div className="mt-2 text-xs font-mono text-cyan-200">{topMomentLabel}</div>
              )}
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-xs font-mono opacity-70">Why this matters</div>
              <div className="text-sm opacity-80 mt-2">
                Use the evidence drawer to review the surrounding context (±60s) and keep the discussion grounded in the same match.
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-xs font-mono opacity-70">What to do next</div>
              <div className="text-sm opacity-80 mt-2">
                Click <span className="font-semibold">Next</span> to open the scouting report: tendencies, how to punish, and draft implications.
              </div>
            </div>
          </div>
        )}

        {(demoGuideStep >= 2) && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-xs font-mono opacity-70">Scouting takeaway</div>
              <div className="mt-1 font-semibold">{patterns?.[0]?.label || 'Scouting report loaded'}</div>
              <div className="text-sm opacity-80 mt-1">{patterns?.[0]?.description || 'Open a pattern to see an evidence-backed example.'}</div>
              <div className="mt-2 text-xs text-slate-300">Confidence is conservative in the demo pack (n=6 → LOW).</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-xs font-mono opacity-70">How to punish</div>
              <div className="text-sm opacity-80 mt-2">
                Use the evidence example to agree on a specific response: where to place vision, when to group, and what timing window to contest.
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-xs font-mono opacity-70">Draft implications</div>
              <div className="text-sm opacity-80 mt-2">
                Treat patterns as hypotheses: if a tendency repeats, consider bans/picks that deny the setup or enable your punish plan.
              </div>
            </div>
          </div>
        )}

        {error && (
          (String(error).toLowerCase().includes('backend not reachable')) ? (
            <div className="bg-rose-950/60 border border-rose-400/20 rounded-2xl p-4">
              <div className="font-semibold">Backend not reachable</div>
              <div className="text-sm text-rose-100/80 mt-1">Run the demo backend and reload.</div>
              <pre className="mt-3 text-xs font-mono bg-black/30 border border-white/10 rounded-xl p-3 overflow-x-auto">
                $env:DEMO_PACK_ROOT="artifacts\\demo_pack"; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
              </pre>
              <div className="text-sm text-rose-100/70 mt-2">Details: {error}</div>
            </div>
          ) : (
            <div className="bg-rose-950/40 border border-rose-400/20 rounded-2xl p-4">
              <div className="font-semibold">Error</div>
              <div className="text-sm text-rose-100/80 mt-1">{error}</div>
            </div>
          )
        )}
        {loading && (
          <div className="text-xs font-mono text-slate-400">Working…</div>
        )}

        {showMethodology && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-sm space-y-2">
            <div className="font-semibold">Coach notes (demo-safe)</div>
            <ul className="list-disc pl-5 space-y-1 opacity-90">
              {datasetInfo && (
                <li>
                  About dataset: source={datasetInfo.source || 'unknown'}; real_matches={datasetInfo.real_matches ?? 'unknown'}; synthetic_matches={datasetInfo.synthetic_matches ?? 'unknown'}.
                </li>
              )}
              <li>All outputs are computed from a frozen demo dataset of 6 matches only (no league-wide claims).</li>
              <li>Critical moments are precomputed deterministically; each match surfaces 3–5 moments with a validity filter and fallback.</li>
              <li>Every evidence link opens an internal evidence panel using a stable internal reference (not shown to judges).</li>
              <li>Evidence context windows are match-scoped (no cross-match context unless explicitly implemented).</li>
              <li>Confidence is sample-size derived: n ≥ 20 → high, 10–19 → medium, &lt; 10 → low (demo uses n=6, so confidence is low).</li>
            </ul>
          </div>
        )}

        {showMethodology && (observationMasking && observationMasking.status !== 'missing') && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-sm">
            <div className="font-semibold mb-2">Context efficiency (observation masking)</div>
            <div className="opacity-80">events_before: {observationMasking.events_before} | events_after: {observationMasking.events_after} | reduction: {observationMasking.reduction_pct}%</div>
          </div>
        )}

        {showMethodology && (benchmarks && benchmarks.status !== 'missing') && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-sm">
            <div className="font-semibold mb-2">Build-time benchmarks</div>
            <div className="opacity-80">pack_build_ms: {benchmarks.pack_build_ms} | integrity_ok: {String(benchmarks.integrity_ok)}</div>
            <div className="mt-2 font-mono text-xs opacity-80 break-all">determinism_sha256: {benchmarks.determinism_sha256_combined}</div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
            <div className="font-semibold mb-3">Critical moments (3–5)</div>
            {moments.length === 0 ? (
              <div className="text-sm opacity-70">Click “Show Critical Moments”.</div>
            ) : (
              <div className="space-y-2">
                {moments.map((m) => (
                  <div key={m.moment_id} className="border border-white/10 rounded-xl p-3 bg-black/20">
                    <div className="flex justify-between gap-3">
                      <div className="font-semibold">{m.title}</div>
                      <div className="text-xs opacity-70">{formatMmSs(m.start_ts)}–{formatMmSs(m.end_ts)}</div>
                    </div>
                    <div className="text-sm opacity-80 mt-1">{m.description}</div>
                    <button
                      className="mt-2 text-sm font-mono text-cyan-200 hover:text-cyan-100"
                      onClick={() => openEvidence(m.primary_event_ref)}
                    >
                      Open evidence @ {formatMmSs(Number(m.start_ts) + 30)}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-4" data-testid="scouting-report">
            <div className="font-semibold mb-3">Scouting report (patterns)</div>
            {patterns.length === 0 ? (
              <div className="text-sm opacity-70">Click “Generate Scouting Report”.</div>
            ) : (
              <div className="space-y-2">
                {patterns.slice(0, 6).map((p, idx) => (
                  <div key={p.pattern_id} className="border border-white/10 rounded-xl p-3 bg-black/20">
                    <div className="flex justify-between">
                      <div className="font-semibold">{p.label}</div>
                      <div className="text-xs font-mono opacity-80">{p.confidence_level.toUpperCase()} (n={p.sample_size})</div>
                    </div>
                    <div className="text-sm opacity-80 mt-1">{p.description}</div>
                    <div className="mt-2 text-xs text-slate-300">Confidence is low here because the demo pack has n=6 matches.</div>
                    {p.instances && p.instances.length > 0 && (
                      <button
                        data-testid={`pattern-evidence-${idx}`}
                        className="mt-2 text-sm font-mono text-cyan-200 hover:text-cyan-100"
                        onClick={() => openEvidence(p.instances[0].evidence_refs[0])}
                      >
                        Open example evidence
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-4" data-testid="integrity-panel">
            <div className="font-semibold mb-3">Verification</div>
            {!integrity ? (
              <div className="text-sm opacity-70">Loading integrity…</div>
            ) : (
              <div className="text-sm space-y-2">
                <div className={integrity.broken_refs === 0 ? 'text-emerald-300 font-semibold' : 'text-rose-300 font-semibold'}>
                  {integrity.broken_refs === 0 ? 'All insights verified ✓' : 'Verification issues found'}
                </div>
                <div className="text-sm text-slate-300">
                  Verification issues:{' '}
                  <span
                    data-testid="broken-refs"
                    className={integrity.broken_refs === 0 ? 'text-emerald-300 font-mono' : 'text-rose-300 font-mono'}
                  >
                    {integrity.broken_refs}
                  </span>
                </div>
                {showMethodology && (
                  <div className="text-xs font-mono opacity-80 space-y-1">
                    <div>total_events: {integrity.total_events}</div>
                    <div>total_moments: {integrity.total_moments}</div>
                    <div>total_patterns: {integrity.total_patterns}</div>
                  </div>
                )}
              </div>
            )}
            <button
              className="mt-3 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg"
              onClick={async () => {
                try {
                  const res = await api.demoIntegrity();
                  setIntegrity(res);
                } catch (e) {
                  setError('Failed to refresh integrity');
                  console.error(e);
                }
              }}
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <EvidenceDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        panel={panel}
      />
    </div>
  );
};

export default DemoDashboard;
