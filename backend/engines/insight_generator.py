def generate_coaching_insights(analytics):
    insights = []
    
    # 1. Cohesion Insight
    cohesion_history = analytics.get('cohesion_history', [])
    if cohesion_history:
        avg_cohesion = sum(c['cohesion_score'] for c in cohesion_history) / len(cohesion_history)
        last_cohesion = cohesion_history[-1]['cohesion_score']
        
        if last_cohesion < avg_cohesion * 0.8:
            insights.append({
                "type": "COHESION",
                "severity": "HIGH",
                "title": "Formation Breakdown",
                "observation": f"Cohesion dropped to {last_cohesion} ({round((1 - last_cohesion/avg_cohesion)*100)}% below average).",
                "recommendation": "Team is overextended. Practice 'Tethering' drills to maintain 1000-unit max spacing during rotations.",
                "impact": "High risk of isolated pick-offs."
            })

    # 2. Risk insight
    risk_score = analytics.get('risk_score', 0)
    if risk_score > 60:
        insights.append({
            "type": "RISK",
            "severity": "CRITICAL",
            "title": "High Criticality Exposure",
            "observation": f"Global risk is {round(risk_score)}%.",
            "recommendation": "Concede non-essential objectives. Reset vision line at T2 towers and wait for power spikes.",
            "impact": "Next fight has <40% win probability."
        })

    # 3. Vision/Pattern Insight
    pattern_history = analytics.get('pattern_history', [])
    if any(p['pattern']['id'] == 'river_control_loss' for p in pattern_history[-5:]):
        insights.append({
            "type": "VISION",
            "severity": "MEDIUM",
            "title": "River Blindness",
            "observation": "Multiple 'River Control Loss' patterns detected.",
            "recommendation": "Invest in 2x Control Wards for Baron/Dragon pit transitions. Priority: Pixel brush control.",
            "impact": "80% of enemy ambushes occur in these zones."
        })

    # Default insight if none generated
    if not insights:
        insights.append({
            "type": "STABILITY",
            "severity": "LOW",
            "title": "Macro Stability Maintained",
            "observation": "Current formation matches historical win signatures.",
            "recommendation": "Continue standard pressure. Maintain current vision coverage.",
            "impact": "Low risk of unexpected reversals."
        })

    return insights
