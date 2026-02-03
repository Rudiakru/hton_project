from backend.engines.causal_analyzer import build_causal_chain

def test_build_causal_chain_negative():
    events = [
        {"type": "dragon_lost", "timestamp": 100},
        {"type": "death_carry", "timestamp": 110}
    ]
    # Observed delta: -10
    chain = build_causal_chain(events, -10)
    assert len(chain) == 2
    assert chain[0]["cause"] == "Dragon Lost"
    assert chain[1]["cause"] == "Death Carry"

def test_build_causal_chain_positive():
    events = [
        {"type": "baron_secured", "timestamp": 200},
        {"type": "kill_carry", "timestamp": 210}
    ]
    # Observed delta: 15
    chain = build_causal_chain(events, 15)
    assert len(chain) == 2
    assert chain[0]["cause"] == "Baron Secured"
    assert chain[1]["cause"] == "Kill Carry"

def test_build_causal_chain_fallback():
    events = []
    chain = build_causal_chain(events, -5)
    assert len(chain) == 1
    assert "Gradual" in chain[0]["cause"]
