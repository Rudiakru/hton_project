# ⚡ ONE-PAGE IMPLEMENTATION CUTLINE SPEC
## Hour-by-Hour Deliverables + Acceptance Tests

> **Purpose:** Prevent scope creep. Every hour has ONE deliverable with PASS/FAIL test.
> **Rule:** If acceptance test fails, fix before moving to next hour.

---

## PRE-HACKATHON (24 Hours Before Judging)

### Hour -24 to -20: Match Selection (PASS/FAIL)

**Deliverable:** 6 clean match files  
**Acceptance Test:**
```python
assert len(demo_matches) == 6
for match in demo_matches:
    assert match.has_timeline_data
    assert match.has_events
    assert not match.is_corrupted
```

---

### Hour -20 to -16: Event Processing + ID Generation (PASS/FAIL)

**Deliverable:** `events_store.json` with stable IDs  
**Acceptance Test:**
```python
# EVIDENCE ID SCHEME (LOCKED): {match_id}:{global_seq:06d}
# Requirement: process_match() must sort events deterministically BEFORE sequencing.

# Test 1: Run twice, IDs must match (determinism on identical raw input)
events_1 = process_match(raw_data)
events_2 = process_match(raw_data)
assert [e.evidence_id for e in events_1] == [e.evidence_id for e in events_2]

# Test 1b: Save/load cycle preserves IDs (guards against refactor drift)
save_events_tmp(events_1)         # write to json/parquet/etc
events_1b = load_events_tmp()     # read back
assert [e.evidence_id for e in events_1b] == [e.evidence_id for e in events_1]

# Test 2: All IDs unique (entire demo pack)
all_ids = [e.evidence_id for e in all_events]
assert len(all_ids) == len(set(all_ids))

# Test 3: ID format (match_id:000042 etc.)
import re
for event in all_events:
    assert re.match(r'^[A-Z0-9-]+:\d{6}$', event.evidence_id)
```

---

### Hour -16 to -12: CPD + Validity Filtering (PASS/FAIL)

**Deliverable:** `moments_store.json` (3–5 coach-valid moments per match; fallback enabled)  
**Acceptance Test:**
```python
for match in demo_matches:
    moments = load_moments(match.id)
    
    # Must surface 3–5 moments PER MATCH (pipeline must add fallback moments if needed)
    assert 3 <= len(moments) <= 5
    
    # All moments must be coach-valid: either passed validity filter OR are explicit fallback with reasons
    for moment in moments:
        assert moment.passes_validity_filter == True
        assert len(moment.validity_reasons) > 0
    
    # All event refs must exist (no broken evidence links)
    event_ids = set(e.evidence_id for e in load_events(match.id))
    for moment in moments:
        assert moment.primary_event_ref in event_ids
        for ref in moment.related_event_refs:
            assert ref in event_ids
```

---

### Hour -12 to -8: Pattern Detection (PASS/FAIL)

**Deliverable:** `patterns_store.json` with evidence refs  
**Acceptance Test:**
```python
patterns = load_patterns("TL")

# Must have 3+ patterns
assert len(patterns) >= 3

# All patterns must have valid structure
for pattern in patterns:
    assert pattern.confidence_level in ["high", "medium", "low"]
    assert 0 <= pattern.frequency <= 1
    assert len(pattern.instances) > 0
    assert pattern.sample_size == 6  # demo dataset size
    
    # All evidence refs must exist
    all_event_ids = set(e.evidence_id for e in load_all_events())
    for instance in pattern.instances:
        for ref in instance.evidence_refs:
            assert ref in all_event_ids
```

---

### Hour -8 to -4: Evidence Panels (PASS/FAIL)

**Deliverable:** `evidence_refs.json` (pre-computed panels)  
**Acceptance Test:**
```python
all_events = load_all_events()

for event in all_events:
    panel = load_evidence_panel(event.evidence_id)
    
    # Panel must exist
    assert panel is not None
    
    # Context window must be from same match
    assert all(e.match_id == event.match_id for e in panel.context_window)
    
    # Related moments must be from same match
    assert all(m.match_id == event.match_id for m in panel.related_moments)
```

---

### Hour -4 to 0: Freeze Artifacts (PASS/FAIL)

**Deliverable:** `demo_pack.tar.gz` ready to deploy  
**Acceptance Test:**
```bash
# Extract in clean directory
tar -xzf demo_pack.tar.gz
cd demo_pack

# Verify structure
assert -f matches/TL-C9-G2.json
assert -f processed/events_store.json
assert -f processed/moments_store.json
assert -f processed/patterns_store.json
assert -f processed/evidence_refs.json

# Run integrity check
python verify_integrity.py
# Must print: "✓ All integrity checks passed"
# Must exit with code 0
```

---

## HACKATHON BUILD (48 Hours)

### Hour 0-3: Project Setup (PASS/FAIL)

**Deliverable:** Docker environment boots in <30s  
**Acceptance Test:**
```bash
# From clean checkout
git clone <repo>
cd <repo>
docker-compose up -d

# Must complete in <30 seconds
# Must print "✓ All services healthy"

# Browser test
curl http://localhost:3000
# Must return 200 OK
```

---

### Hour 3-6: Load Demo Pack (PASS/FAIL)

**Deliverable:** All data in database  
**Acceptance Test:**
```sql
-- Events loaded
SELECT COUNT(*) FROM events;
-- Must return >0

-- Moments loaded
SELECT COUNT(*) FROM moments;
-- Must return 18-30 (3-5 per match × 6 matches)

-- Patterns loaded
SELECT COUNT(*) FROM patterns;
-- Must return >=6 (3+ per team × 2 teams)

-- Evidence panels loaded
SELECT COUNT(*) FROM evidence_panels;
-- Must match event count

-- No broken references
SELECT COUNT(*) FROM moments m
WHERE NOT EXISTS (
    SELECT 1 FROM events e 
    WHERE e.evidence_id = m.primary_event_ref
);
-- Must return 0
```

---

### Hour 6-9: Match/Team Selectors (PASS/FAIL)

**Deliverable:** UI with working dropdowns  
**Acceptance Test:**
```javascript
// Automated UI test
cy.visit('http://localhost:3000')

// Match selector exists and works
cy.get('#match-selector').should('exist')
cy.get('#match-selector').select('TL-C9-G2')
cy.get('#match-selector').should('have.value', 'TL-C9-G2')

// Team selector exists and works
cy.get('#team-selector').should('exist')
cy.get('#team-selector').select('TL')
cy.get('#team-selector').should('have.value', 'TL')
```

---

### Hour 9-12: Query Router (PASS/FAIL)

**Deliverable:** All routes return data without errors  
**Acceptance Test:**
```javascript
// Test show_moments
const moments = await queryRouter.route({
    match_id: 'TL-C9-G2',
    action: 'show_moments'
});
assert(moments.length >= 3);
assert(moments.length <= 5);

// Pick a real evidence_id from returned moments (NO hardcoded IDs)
const evidenceId = (moments[1] && moments[1].primary_event_ref) || moments[0].primary_event_ref;
assert(typeof evidenceId === 'string' && evidenceId.length > 0);

// Test analyze_moment
const analysis = await queryRouter.route({
    match_id: 'TL-C9-G2',
    evidence_id: evidenceId,
    action: 'analyze_moment'
});
assert(analysis.panel_data !== null);
assert(analysis.panel_data.event.evidence_id === evidenceId);

// Test scout_team
const report = await queryRouter.route({
    team_id: 'TL',
    action: 'scout_team'
});
assert(report.patterns.length >= 3);
```

---

### Hour 12-16: Evidence Panel Component (PASS/FAIL)

**Deliverable:** Evidence panel renders all data  
**Acceptance Test:**
```javascript
cy.visit('http://localhost:3000')

// Navigate to a moment
cy.get('#match-selector').select('TL-C9-G2')
cy.contains('Show Critical Moments').click()
cy.contains('18:40').click()  // Click moment

// Panel must open
cy.get('[data-testid="evidence-panel"]').should('be.visible')

// Must show event details
cy.get('[data-testid="event-type"]').should('contain.text', 'CHAMPION_KILL')
cy.get('[data-testid="timestamp"]').should('contain.text', '18:40')

// Must show context window
cy.get('[data-testid="context-events"]').children().should('have.length.greaterThan', 0)

// Must show related moments
cy.get('[data-testid="related-moments"]').children().should('have.length.greaterThan', 0)
```

---

### Hour 16-20: Moment Timeline UI (PASS/FAIL)

**Deliverable:** Timeline shows 3-5 moments  
**Acceptance Test:**
```javascript
cy.visit('http://localhost:3000')
cy.get('#match-selector').select('TL-C9-G2')
cy.contains('Show Critical Moments').click()

// Timeline renders
cy.get('[data-testid="timeline"]').should('be.visible')

// Has 3-5 moments
cy.get('[data-testid="moment-marker"]').should('have.length.greaterThan', 2)
cy.get('[data-testid="moment-marker"]').should('have.length.lessThan', 6)

// Each moment is clickable
cy.get('[data-testid="moment-marker"]').first().click()
cy.get('[data-testid="evidence-panel"]').should('be.visible')
```

---

### Hour 20-24: Scouting Report UI (PASS/FAIL)

**Deliverable:** Report displays patterns with evidence  
**Acceptance Test:**
```javascript
cy.visit('http://localhost:3000')
cy.get('#team-selector').select('TL')
cy.contains('Generate Scouting Report').click()

// Report loads
cy.get('[data-testid="scouting-report"]').should('be.visible')

// Has patterns
cy.get('[data-testid="pattern-card"]').should('have.length.greaterThan', 2)

// Each pattern has confidence badge
cy.get('[data-testid="confidence-badge"]').should('exist')

// Each pattern has evidence links
cy.get('[data-testid="evidence-link"]').should('have.length.greaterThan', 0)

// Evidence link works
cy.get('[data-testid="evidence-link"]').first().click()
cy.get('[data-testid="evidence-panel"]').should('be.visible')
```

---

### Hour 24-28: Status Banner + Methodology (PASS/FAIL)

**Deliverable:** Trust elements visible on all pages  
**Acceptance Test:**
```javascript
// Status banner on every page
const pages = ['/', '/moments', '/scout', '/methodology']
for (const page of pages) {
    cy.visit(`http://localhost:3000${page}`)
    
    // Banner visible
    cy.get('[data-testid="status-banner"]').should('be.visible')
    cy.get('[data-testid="status-banner"]').should('contain.text', 'Demo Mode')
    cy.get('[data-testid="status-banner"]').should('contain.text', '6 matches')
}

// Methodology page exists
cy.visit('http://localhost:3000/methodology')
cy.contains('What is a Critical Moment?').should('be.visible')
cy.contains('What is a Pattern?').should('be.visible')
cy.contains('How are Baselines Computed?').should('be.visible')
```

---

### Hour 28-32: Health Panel (PASS/FAIL)

**Deliverable:** System health metrics display  
**Acceptance Test:**
```javascript
cy.visit('http://localhost:3000')

// Health panel visible
cy.get('[data-testid="health-panel"]').should('be.visible')

// Shows event count
cy.get('[data-testid="health-events"]').should('contain.text', /\d+/)

// Shows moment count
cy.get('[data-testid="health-moments"]').should('contain.text', /\d+/)

// Shows zero broken refs
cy.get('[data-testid="health-broken-refs"]').should('contain.text', '0')
cy.get('[data-testid="health-broken-refs"]').parent().find('[data-testid="status-ok"]').should('exist')
```

---

### Hour 32-36: End-to-End Demo Test (PASS/FAIL)

**Deliverable:** Complete demo flow works  
**Acceptance Test:**
```javascript
// CRITICAL PATH TEST - Must pass 10 times in a row

for (let i = 0; i < 10; i++) {
    // Restart browser
    cy.visit('http://localhost:3000')
    
    // Demo Step 1: Show moments
    cy.get('#match-selector').select('TL-C9-G2')
    cy.contains('Show Critical Moments').click()
    cy.get('[data-testid="moment-marker"]').should('have.length.greaterThan', 2)
    
    // Demo Step 2: Analyze moment
    cy.get('[data-testid="moment-marker"]').eq(1).click()
    cy.get('[data-testid="evidence-panel"]').should('be.visible')
    
    // Demo Step 3: Scout team
    cy.get('#team-selector').select('TL')
    cy.contains('Generate Scouting Report').click()
    cy.get('[data-testid="pattern-card"]').should('have.length.greaterThan', 2)
    
    // Demo Step 4: Evidence drilldown
    cy.get('[data-testid="evidence-link"]').first().click()
    cy.get('[data-testid="evidence-panel"]').should('be.visible')
}

// If any iteration fails, FIX before continuing
```

---

### Hour 36-40: Documentation (PASS/FAIL)

**Deliverable:** README with working setup  
**Acceptance Test:**
```bash
# Clean machine test
docker system prune -af
rm -rf /tmp/hackathon-test
cd /tmp/hackathon-test

# Follow README exactly
cat README.md | grep "Quick Start" -A 20 > setup.sh
bash setup.sh

# Must result in working app
curl http://localhost:3000
# Must return 200

# UI must load
curl http://localhost:3000 | grep "Demo Mode"
# Must match
```

---

### Hour 40-44: Buffer (MUST EXIST)

**Deliverable:** Nothing new - fix any broken tests  
**Acceptance Test:**
```bash
# Re-run ALL previous acceptance tests
# ALL must pass
pytest tests/
cypress run

# Exit code must be 0
```

---

### Hour 44-48: Final Submission (PASS/FAIL)

**Deliverable:** Submitted to Devpost  
**Acceptance Test:**
```bash
# Video recorded
assert -f demo_video.mp4
# Must be 2-3 minutes
# Must show complete demo flow

# Devpost submitted
# Screenshot of confirmation page required

# Backup plan ready
assert -f backup_video.mp4
assert -f backup_slides.pdf
```

---

## CRITICAL CUTLINE RULES

### Rule 1: NO SCOPE CREEP
If it's not in this spec, **DON'T BUILD IT**.

### Rule 2: NO MOVING FORWARD WITHOUT PASS
Every acceptance test must PASS before next hour.

### Rule 3: NO OPTIMISTIC ASSUMPTIONS
If test is red, assume it will stay red until fixed.

### Rule 4: BUFFER IS SACRED
Do NOT use buffer hours for new features.

### Rule 5: DEMO FLOW IS KING
The end-to-end demo test (Hour 32-36) is the ONLY thing that matters.

---

## DEFINITION OF DONE

The project is done when:

```bash
# All tests pass
pytest tests/ --exitcode 0
cypress run --exitcode 0

# Demo flow passes 10x
npm run test:demo:critical -- --iterations 10 --exitcode 0

# Zero broken references
psql -c "SELECT COUNT(*) FROM broken_refs;" | grep " 0"

# Clean machine works
./scripts/clean_machine_test.sh --exitcode 0

# Submission complete
[ -f submission_confirmation.png ]
```

**If any of these fail, you are NOT done.**

---

## ESCAPE HATCHES (If Running Behind)

### If behind at Hour 12:
- Cut "natural language query" feature
- Keep: selectors + buttons only
- Impact: -0.5 points (acceptable)

### If behind at Hour 24:
- Cut health panel
- Keep: status banner + methodology
- Impact: -0.5 points (acceptable)

### If behind at Hour 36:
- Use cached demo flow (pre-recorded interactions)
- Impact: -1.0 points (risky but survivable)

### If behind at Hour 44:
- Submit backup video only
- Impact: -2.0 points (you might not place)

---

**FOLLOW THIS SPEC EXACTLY. NO DEVIATIONS. YOU WILL FINISH.**

# ⚡ ONE-PAGE IMPLEMENTATION CUTLINE SPEC
## Hour-by-Hour Deliverables for a Bulletproof Hackathon Win (V2)

**North Star:** A deterministic, offline demo that cannot fail on stage.

**Hard constraints:**
- Demo runs with **zero internet**
- Demo uses **no runtime LLM calls**
- Demo uses **no heavy compute at runtime**
- Every insight has **internal evidence drilldown**
- Integrity check must show `broken_refs == 0`

---

# 0) HARD CUTLINE — WHAT WE SHIP

## MUST SHIP (non-negotiable)
1. **Frozen Demo Pack** (`demo_pack.tar.gz`)
2. **Deterministic Evidence IDs** everywhere
3. **3–5 Coach-plausible Moments per match**
4. **Scouting Report UI** (team selector → report → evidence)
5. **Evidence Drawer** (internal, match-scoped ±60s context)
6. **Integrity Panel** (health + broken refs + dataset scope)
7. **Start Demo flow** (single safe stage path)

## MUST NOT SHIP (kills you)
- Live tool-calling agent
- External replay links
- League-wide baselines
- Win probability
- Causal claims
- Anything stochastic during demo

---

# 1) CANONICAL DATA CONTRACT (LOCKED)

## Evidence IDs (locked format)
**Format:** `{match_id}:{global_seq:06d}`  
Example: `TL-C9-G2:000042`

**Determinism rule:**
- Sort events deterministically
- Then assign global sequence

**Sort key order (locked):**
1. timestamp_ms
2. event_type
3. stable payload hash (e.g., sha1 of canonical JSON)
4. raw_index fallback

---

# 2) DEMO PACK CONTENTS (LOCKED)

`demo_pack/`
- `processed/events_store.json`
- `processed/moments_store.json`
- `processed/patterns_store.json`
- `processed/evidence_refs.json`
- `reports/*.json`
- `cached_queries/*.json`
- `verify_integrity.py` (self-contained, no repo imports)

**Demo dataset:** exactly **6 matches** (frozen)

---

# 3) MOMENT GENERATION (DETERMINISTIC)

**Goal:** Always produce **3–5** moments per match that feel coach-plausible.

## Pipeline:
1. Extract event-based features at windows (deterministic)
2. Produce candidate moments (simple changepoint OR heuristics)
3. Apply **Validity Filter**
4. If fewer than 3, apply fallback rules to fill up
5. If more than 5, rank + keep top 5

## Validity Filter (passes if ANY true in ±90s window)
- Objective event exists (dragon/baron/tower/inhib)
- ≥2 champion kills
- abs(gold_swing_60s) ≥ 1500
- ≥3 ward events (placed/killed)
- structure event exists

## Fallback if too few moments
- pick top-k windows by gold swing
- add first objective event window
- add first multi-kill window
- add first vision battle window

---

# 4) PATTERN DETECTION (DEMO ONLY)

**Scope:** Patterns are computed *only inside demo dataset*.

Rules:
- `sample_size == 6` for demo
- confidence level derived from sample size:
  - `n ≥ 20 high`
  - `10–19 medium`
  - `<10 low`  ← demo will be low (explain why)

Display:
- Main view: k/n + baseline + confidence badge
- Drilldown: Wilson CI + limitations

---

# 5) EVIDENCE PANEL (MATCH-SCOPED)

For every `evidence_id`, precompute panel payload:

- event details
- context_window: ±60s events **from the same match only**
- feature snapshot at event time
- related moments: moments in same match near timestamp

**No cross-match contamination.**
This gets contract-tested.

---

# 6) BACKEND API (DEMO MODE ONLY)

All demo endpoints read exclusively from `DEMO_PACK_ROOT`:

- `GET /api/demo/health`
- `GET /api/demo/matches`
- `GET /api/demo/teams`
- `GET /api/demo/show-moments?match_id=...`
- `GET /api/demo/analyze-moment?evidence_id=...`
- `GET /api/demo/scout-team?team_id=...`
- `GET /api/demo/integrity`

**Integrity output must include:**
- match count == 6
- total events
- total moments
- broken_refs == 0

---

# 7) FRONTEND: STAGE-SAFE FLOW

Demo UI is selector-first (no NL ambiguity).

**Stage path (single safe path):**
1) Click `Start Demo`
   - select hero match/team
   - load moments
   - open evidence drawer for top moment
2) Click `Next`
   - open scouting report
   - open first pattern evidence instance
3) Click `Integrity`
   - show `broken_refs: 0`
   - show dataset scope note
   - show offline mode note

**Never show evidence_id raw to judges** (show match+time instead).

---

# 8) AUTOMATED PROOFS (JUDGE-PROOF)

Must pass:
1) **Double-build determinism** → packs identical
2) **Match-scoped evidence panels** → no cross-match events
3) **10× critical demo flow** → no flake
4) **Failure-mode surfacing** → corrupted pack shows actionable errors

---

# 9) FINAL “WINNING” ADD-ONS (ALLOWED)

Only implement if they do not add runtime risk:
- validation section (manual labeling on 2 matches)
- coaching value story + ROI
- coach-language UI copy pass
- screenshots + 90s backup video

---

# 10) ACCEPTANCE CHECKLIST (SHIP GATE)

- [ ] Demo pack builds deterministically twice
- [ ] verify_integrity.py passes offline
- [ ] pytest passes
- [ ] Start Demo path works 10 times manually
- [ ] Evidence drawer opens for every click
- [ ] Scouting report evidence links work
- [ ] Integrity shows broken_refs == 0
- [ ] README includes: value story + validation + limitations
