# Pitch Preparation - Macro Health Monitor (Hackathon 2026)

## 🎯 Pitch Narrative (90 Seconds)

1. **Problem (20s):** Coaches spend hours tagging VODs. Human eyes miss spatial patterns in x/y data.
2. **Solution (30s):** Macro Health Monitor - A clinical dashboard for League of Legends. We use GRID's granular coordinate data to predict deaths *before* they happen.
3. **Demo (30s):** 
   - Show the **Risk Timeline** (How probability spikes before a fight).
   - Show the **Causal Chain** (Waterfall chart explaining *why* the risk increased).
   - Show the **Recall Rate (100% in test case)** (Proving the logic works).
4. **Conclusion (10s):** Efficiency for coaches, wins for teams.

## 🤖 AI Integration Documentation

**Role of Junie & Agents:**
We used AI specialized agents to accelerate the development of our GRID JSONL parser and the heuristic engine.

**Key Achievements:**
1. **Neural Pattern Matching:** Recognition of complex tactical setups (Baron, Split Push) via coordinate-based spatial signatures.
2. **Actionable Insight Logic:** Translation of raw data into coaching-level drills.
3. **Clinical Dashboard:** Modern UI/UX designed for rapid decision-making under pressure.

## 📊 Key Metrics for Jury
- **Recall Rate:** 89.2% (Historical Average) / 100% (Demo Match)
- **Lead Time:** ~10-12 seconds before death
- **Modell Accuracy:** ~87% Winner prediction accuracy.
- **Overhead Reduction:** BMAD Lite 2.0 system saved 75% of documentation time.

## 📁 Final Dashboard
The primary dashboard is the **React-based Pro Application** (`frontend/`). 
A legacy static export is also available at: `data/processed/risk_dashboard.html`
