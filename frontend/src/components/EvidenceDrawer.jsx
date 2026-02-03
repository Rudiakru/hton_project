import React from 'react';

const EvidenceDrawer = ({ open, onClose, panel }) => {
  if (!open) return null;

  const event = panel?.event;
  const context = panel?.context_window || [];
  const relatedMoments = panel?.related_moments || [];

  const formatMmSs = (tsSeconds) => {
    const s = Math.max(0, Number(tsSeconds) || 0);
    const mm = Math.floor(s / 60);
    const ss = Math.floor(s % 60);
    return `${mm}:${String(ss).padStart(2, '0')}`;
  };

  const formatMatchLabel = (matchId) => {
    if (!matchId || typeof matchId !== 'string') return '';
    const parts = matchId.split('-');
    if (parts.length < 3) return matchId;
    const a = parts[0];
    const b = parts[1];
    const g = parts[2];
    const gameNum = (g && g.toUpperCase().startsWith('G')) ? g.slice(1) : g;
    return `${a} vs ${b} • Game ${gameNum}`;
  };

  const matchId = panel?.match_id || event?.match_id || '';
  const timeLabel = event?.game_time || (typeof event?.ts === 'number' ? formatMmSs(event.ts) : '');
  const headerTitle = `${formatMatchLabel(matchId)}${timeLabel ? ` @ ${timeLabel}` : ''}`.trim();

  return (
    <div className="fixed inset-0 z-50 pointer-events-none" data-testid="evidence-drawer">
      {/*
        In demo mode we keep this drawer non-blocking: judges should be able to keep
        clicking the main demo path (Start Demo → Next) while evidence is open.
      */}
      <div className="absolute inset-0 bg-black/40 pointer-events-none" />
      <div className="absolute right-0 top-0 h-full w-full max-w-xl bg-slate-950 text-white shadow-2xl border-l border-white/10 overflow-y-auto custom-scrollbar pointer-events-auto">
        <div className="p-4 border-b border-white/10 flex justify-between items-center">
          <div>
            <div className="text-xs opacity-70">Moment evidence</div>
            <div className="text-lg font-bold" data-testid="evidence-title">{headerTitle || 'Moment evidence'}</div>
            <div className="text-xs text-slate-300 mt-1">Internal-only proof panel (offline). Match-scoped context window.</div>

            {/* Keep the stable test hook, but never show raw evidence ids to judges. */}
            <details className="mt-2 text-xs">
              <summary className="cursor-pointer opacity-70 hover:opacity-90 select-none">Technical details</summary>
              <div className="mt-2 font-mono bg-black/30 border border-white/10 rounded-lg p-2 overflow-x-auto">
                <div className="opacity-70">Internal reference (coach-safe)</div>
                <div data-testid="evidence-id">{headerTitle || 'Hidden'}</div>
              </div>
            </details>
          </div>
          <button className="px-3 py-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="p-4 space-y-4" data-testid="evidence-panel">
          <section className="bg-white/5 rounded-xl p-3 border border-white/10">
            <div className="text-sm font-semibold mb-2">Event details</div>
            {event ? (
              <div className="text-sm space-y-1">
                <div><span className="opacity-70">Match:</span> {formatMatchLabel(event.match_id) || event.match_id}</div>
                <div><span className="opacity-70">Time:</span> {event.game_time || formatMmSs(event.ts)}</div>
                <div><span className="opacity-70">Signal:</span> {event.event_type}</div>
              </div>
            ) : (
              <div className="text-sm opacity-70">No event data</div>
            )}
          </section>

          <section className="bg-white/5 rounded-xl p-3 border border-white/10">
            <div className="text-sm font-semibold mb-2">±60s context window (match-scoped)</div>
            <div className="space-y-2">
              {context.length === 0 ? (
                <div className="text-sm opacity-70">No context events</div>
              ) : (
                context.map((e) => (
                  <div key={`${e.match_id}-${e.ts}-${e.event_type}`} className="text-sm border border-white/10 rounded-lg p-2 bg-black/20">
                    <div className="flex justify-between">
                      <div className="text-xs text-slate-300">{e.game_time || formatMmSs(e.ts)}</div>
                      <div className="opacity-70">{e.event_type}</div>
                    </div>
                    <div className="opacity-80 text-slate-200 mt-1">{e.payload?.label || e.payload?.pattern_id || ''}</div>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="bg-white/5 rounded-xl p-3 border border-white/10">
            <div className="text-sm font-semibold mb-2">Related moments (match-scoped)</div>
            <div className="space-y-2">
              {relatedMoments.length === 0 ? (
                <div className="text-sm opacity-70">No related moments</div>
              ) : (
                relatedMoments.map((m) => (
                  <div key={m.moment_id} className="text-sm border border-white/10 rounded-lg p-2 bg-black/20">
                    <div className="flex justify-between">
                      <div className="font-semibold">{m.title}</div>
                      <div className="opacity-70">{formatMmSs(m.start_ts)}–{formatMmSs(m.end_ts)}</div>
                    </div>
                    <div className="opacity-80">{m.description}</div>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default EvidenceDrawer;
