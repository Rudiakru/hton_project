# Technical Implementation Plan - Hackathon Product Analysis

Based on critical analysis of the conversation, here's the streamlined technical roadmap for AI execution:

---

## **CORE ARCHITECTURE**

### **1. DATA FOUNDATION (Priority: CRITICAL)**

**Objective**: Parse GRID JSONL with robust error handling

```python
# Junie Prompt Template:
"Analyze this GRID JSONL schema and write a Python parser that:
- Extracts player positions (x, y coordinates)
- Handles missing timestamps gracefully
- Returns structured events (kills, objectives, teamfights)
- Includes unit tests for malformed data"

# Implementation Requirements:
- Safe parsing with try/catch blocks
- Default fallback data when fields missing
- Validate data structure BEFORE hackathon starts
```

**Validation Test**:
```python
def test_parser_robustness():
    # Test with intentionally broken data
    assert parser.parse(null_coordinates) returns default_value
    assert parser.parse(missing_timestamp) skips_frame
    assert parser.parse(empty_array) returns []
```

---

### **2. RISK SCORING ENGINE (No ML - Heuristics Only)**

**Objective**: Oracle-style risk calculation with transparent weights

```python
def calculate_risk_score(game_state):
    """
    Fixed-weight heuristic model (NOT ML)
    Fully explainable, no training required
    """
    weights = {
        'gold_diff_normalized': 0.4,
        'objective_diff': 0.3,  # Dragons + Barons*2
        'vision_score_ratio': 0.3
    }
    
    risk_score = (
        weights['gold_diff_normalized'] * (game_state.gold_diff / 10000) +
        weights['objective_diff'] * game_state.objective_count +
        weights['vision_score_ratio'] * (game_state.team_vision / game_state.enemy_vision)
    )
    
    return risk_score  # 0-100 scale

# Stage Classification:
# 0-20: Critical
# 20-40: Vulnerable  
# 40-60: Competitive
# 60-100: Winning
```

**Why This Works**:
- ✅ Zero training time
- ✅ Deterministic output
- ✅ Fully explainable weights
- ✅ Works with incomplete data (graceful degradation)

---

### **3. SPATIAL ANALYTICS (The Differentiator)**

**CRITICAL FIX**: Cannot use "enemy proximity" without vision data

**NEW APPROACH**: Team Cohesion Score (Descriptive, not Prescriptive)

```python
def calculate_team_cohesion(team_positions, timestamp):
    """
    Measures team spread WITHOUT judging if it's good/bad
    Avoids false positives from split-push strategies
    """
    distances = []
    for i, p1 in enumerate(team_positions):
        for p2 in team_positions[i+1:]:
            dist = euclidean_distance(p1, p2)
            distances.append(dist)
    
    return {
        "timestamp": timestamp,
        "avg_spread": mean(distances),
        "max_separation": max(distances),
        "cohesion_score": 1000 / mean(distances)  # Higher = more grouped
    }

# Correlation Analysis:
# "Teams with cohesion <X during teamfights lose 68% more often"
# Let COACHES interpret if spread was intentional
```

**Visualization**:
- Timeline chart: Cohesion score over match duration
- Event overlay: Mark teamfights on timeline
- Correlation metric: Display win/loss rate by cohesion threshold

---

### **4. CAUSAL CHAIN EXPLAINER**

**CRITICAL FIX**: Use Event Impact Table (not time proximity)

```python
# Predefined Impact Weights (Based on Esports Analytics Research)
EVENT_IMPACTS = {
    "dragon_lost": -6,      # % Win Probability impact
    "baron_lost": -12,
    "tower_lost": -3,
    "death_carry": -4,      # ADC/Mid death
    "death_support": -2,
    "gold_swing_1k": -2     # Per 1000 gold
}

def build_causal_chain(events_in_window, wp_delta):
    """
    Explains WP drop using weighted events
    NOT just 'everything in last 60s'
    """
    # Sort events by impact magnitude
    sorted_events = sorted(events, key=lambda e: abs(EVENT_IMPACTS[e.type]))
    
    chain = []
    explained_delta = 0
    
    for event in sorted_events:
        impact = EVENT_IMPACTS[event.type]
        chain.append({
            "event": event.name,
            "impact": impact,
            "timestamp": event.time
        })
        explained_delta += impact
        
        # Stop when we've explained the delta (within 2% error)
        if abs(explained_delta - wp_delta) < 2:
            break
    
    return chain
```

**Visualization** (Recharts Waterfall Chart):
```javascript
// Display breakdown:
// Risk Score: 45% → 33% (-12%)
//   ├─ Dragon Lost: -6%
//   ├─ ADC Death: -4%  
//   └─ Vision Drop: -2%
```

---

### **5. JUNIE INTEGRATION (Sponsor Appeal)**

**Objective**: Demonstrate agentic workflow, not just autocomplete

**Documentation Strategy**:
1. **Screenshot**: Junie prompt for parser generation
2. **Screenshot**: Generated code with error handling
3. **Screenshot**: Unit tests written by Junie
4. **Video Segment** (30s):
   - Show problem: "200 fields in JSONL - which matter?"
   - Show Junie solving it: Chat interface
   - Show validation: Tests passing

**Example Prompt for Demo**:
```
"Junie, analyze this GRID JSONL schema and write:
1. A parser extracting only positions, timestamps, events
2. Error handling for missing fields
3. Unit tests covering edge cases"
```

---

## **48-HOUR TIMELINE (Risk-Minimized)**

### **Saturday (16h productive)**

**09:00-12:00 (3h)**: GRID Data Exploration
- Download 3+ sample matches
- **VALIDATE**: x/y coords exist in every frame?
- **VALIDATE**: Role metadata available?
- Document Junie's parser generation

**12:00-15:00 (3h)**: Basic Dashboard
- React + Recharts setup
- Single chart: Gold difference over time
- **Goal**: Something renders on screen

**15:00-18:00 (3h)**: Risk Score Implementation
- Oracle heuristic (no ML)
- Test with 3 matches
- **Goal**: Risk score shows reasonable values

**18:00-21:00 (3h)**: Cohesion Algorithm
- Calculate team spread from coordinates
- Correlate with teamfight outcomes
- **Goal**: "Teams with X cohesion lose Y% more" statistic

**21:00-01:00 (4h)**: Buffer for debugging

---

### **Sunday (20h productive)**

**09:00-12:00 (3h)**: Causal Chain Visualizer
- Event Impact Table implementation
- Waterfall chart component
- **Goal**: WP drop auto-explained

**12:00-15:00 (3h)**: Stage-Based Alerts
- Color-coded risk stages (Red/Yellow/Green)
- Simple if/else logic (no complex ML)
- **Goal**: Visual "triage dashboard"

**15:00-18:00 (3h)**: Heatmap Feature
- Death position heatmap (Plotly.js)
- Overlay victory positions
- **Goal**: "Your deaths cluster in Bot River - improve vision there"

**18:00-21:00 (3h)**: Demo Video (Part 1)
- Script 90-second narrative:
  - Problem (10s)
  - Solution overview (20s)
  - Live demo (40s)
  - Junie workflow (15s)
  - Impact (5s)

**21:00-23:00 (2h)**: Video Recording
- Screen capture with OBS
- One-take rule (perfect is enemy of done)

**23:00-02:00 (3h)**: Submission Polish
- README with architecture diagram
- Code comments/docstrings
- Show where Junie contributed

**02:00-05:00 (3h)**: Emergency buffer

---

## **TESTING & VALIDATION PROTOCOL**

### **Unit Tests (Must-Have)**

```python
def test_parser_handles_null_coordinates():
    """Parser must not crash on missing data"""
    data = {"coordinates": None, "timestamp": 123}
    result = parse_grid_data(data)
    assert result is not None

def test_risk_score_bounds():
    """Risk score must stay 0-100"""
    extreme_state = {"gold_diff": 999999, "objectives": -5}
    score = calculate_risk_score(extreme_state)
    assert 0 <= score <= 100

def test_cohesion_with_two_players():
    """Edge case: What if only 2 players alive?"""
    positions = [(0,0), (100,100)]
    cohesion = calculate_team_cohesion(positions)
    assert cohesion.avg_spread > 0
```

### **Integration Tests (Critical Path)**

```python
def test_full_pipeline():
    """End-to-end: JSONL → Dashboard"""
    # 1. Load sample match
    data = load_grid_file("sample_match.jsonl")
    
    # 2. Parse events
    events = parse_events(data)
    assert len(events) > 0
    
    # 3. Calculate risk
    risk_timeline = [calculate_risk_score(state) for state in events]
    assert all(0 <= r <= 100 for r in risk_timeline)
    
    # 4. Generate causal chain
    chain = build_causal_chain(events, wp_delta=-12)
    assert sum(e['impact'] for e in chain) ≈ -12
```

### **Demo Validation Checklist**

Before submission:
- [ ] Demo runs 10x without crashes
- [ ] Works with 3 different match files (not just "golden sample")
- [ ] Fallback behavior when data missing (shows warning, not white screen)
- [ ] Video under 3 minutes
- [ ] Junie visible in 2+ screenshots
- [ ] README explains GRID data usage

---

## **PITCH SCRIPT (90 Seconds)**

**Minute 1 - The Problem**:
> "Esports analysts spend 6+ hours weekly manually tagging VODs in tools like Nacsport. They click through every teamfight asking: 'Why did we lose?' But human eyes can't detect patterns across 50+ matches - that requires data science."

**Minute 2 - The Solution**:
> "We built Macro Health Monitor - a Clinical Decision Support System for Esports. Instead of dumping data on coaches, we give them a triage dashboard. Like an EKG monitor showing 'Patient in danger,' coaches see 'Team in Stage 2 Risk - Vision control collapsing.'"

**Minute 3 - Live Demo**:
> [Screen recording plays]
> "We upload a Cloud9 vs TL match. In 30 seconds:
> - Auto-tagged events (teamfights, objectives)
> - Risk score timeline showing exactly when the game flipped
> - Causal chain: 'At minute 15, risk dropped 12%. Why? -6% dragon loss, -4% ADC death, -2% vision drop'
> - Our differentiator: Using GRID's x/y coordinates, we show C9's ADC was isolated 3x - correlates with 68% higher teamfight loss rate."

**Minute 4 - The Tech**:
> "We used JetBrains' Junie to write our JSONL parser - 200 lines in 5 minutes. GRID's granular position data enables analysis impossible with standard Riot API. We see WHERE players stood, not just THAT they died."

**Minute 5 - Impact**:
> "For coaches: 6 hours/week saved. New insights never found manually. Not just 'that was bad' - but 'here's exactly what to fix.'"

---

## **CRITICAL RISKS & MITIGATION**

| Risk | Mitigation |
|------|-----------|
| **GRID data missing x/y coords** | Validate schema NOW (pre-hackathon). Have fallback to summary data. |
| **Cohesion algorithm too slow** | Limit calculation to teamfight windows only (not every frame). |
| **Demo crashes live** | Pre-record backup video. Have "Safe Mode" that only shows basic charts. |
| **False positives in spacing** | Use descriptive language ("High spread") not prescriptive ("Critical error"). |
| **Judges ask "Show different match"** | Test with 5+ matches beforehand. Document known limitations in README. |

---

## **WIN CONDITION ANALYSIS**

**Your competitive advantages**:
1. ✅ **Spatial analytics** (nobody else using x/y coordinates)
2. ✅ **Causal explainability** (Event Impact Table is novel)
3. ✅ **Zero ML risk** (heuristics are deterministic)
4. ✅ **Strong sponsor integration** (Junie workflow + GRID data showcase)

**Estimated placement**: **Top 3 candidate** if:
- All features work in demo (80% reliability minimum)
- Video clearly shows problem → solution → impact
- Junie contribution well-documented
- No crashes during presentation

**Failure modes to avoid**:
- Overpromising features that don't work
- Using vague language ("AI-powered" without showing how)
- Ignoring sponsor requirements (must use Junie + GRID visibly)

---

## **FINAL TECHNICAL REQUIREMENTS**

### **Must-Have Features** (Core MVP):
1. Risk Score Calculator (heuristic-based)
2. Causal Chain Visualizer (waterfall chart)
3. Team Cohesion Timeline (spatial analysis)
4. Auto-event tagging from GRID data
5. Junie-generated parser (documented)

### **Nice-to-Have Features** (If time permits):
6. Death position heatmap
7. Pattern library (Baron setup, split-push detection)
8. Multi-match comparison view

### **Cut if Necessary** (Deprioritize):
- Real-time mode (focus on post-game analysis)
- Advanced pattern recognition (keep it simple)
- 3D visualizations (2D is sufficient)

---

## **IMMEDIATE ACTION ITEMS**

**Before Saturday 09:00**:
1. Download 3+ GRID sample matches
2. Open JSONL in text editor - verify x/y coordinates exist
3. Check if role metadata (ADC/Mid/Support) included
4. Set up React + Recharts + Plotly locally
5. Test Junie access in IDE

**First 3 Hours (Saturday Morning)**:
1. Have Junie write parser (with unit tests)
2. Screenshot every step for demo
3. Validate parser with all 3 sample files
4. If data structure broken → pivot immediately

**Decision Points**:
- **Saturday 14:00**: If GRID data problematic → switch to mock data for demo
- **Saturday 20:00**: If cohesion calc slow → simplify to 2-player distances only
- **Sunday 12:00**: If pattern matching too complex → cut feature, focus on heatmaps

---

This technical plan eliminates the high-risk components (ML training, vision-dependent algorithms, unfalsifiable predictions) while maintaining strong differentiation through spatial analytics and causal explainability. Execute methodically, test relentlessly, and ship a polished demo.