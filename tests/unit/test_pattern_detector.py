from backend.engines.pattern_detector import detect_patterns

def test_detect_baron_setup():
    # Near Baron pit after 20 mins
    positions = [
        {'x': 5100, 'y': 10100},
        {'x': 4900, 'y': 9900},
        {'x': 5000, 'y': 10000},
        {'x': 5200, 'y': 10200},
        {'x': 4800, 'y': 9800}
    ]
    # 1200 seconds = 20:00
    detected = detect_patterns(positions, 1210)
    assert any(p['id'] == 'baron_setup' for p in detected)

def test_detect_split_push_1_4():
    # 1 Top, 4 Mid
    positions = [
        {'x': 1000, 'y': 10000}, # Top
        {'x': 7000, 'y': 7000},  # Mid
        {'x': 7100, 'y': 7100},  # Mid
        {'x': 7200, 'y': 7200},  # Mid
        {'x': 7300, 'y': 7300}   # Mid
    ]
    detected = detect_patterns(positions, 600)
    assert any(p['id'] == 'split_push_1_4' for p in detected)

def test_detect_river_control_loss():
    # 3 in River, vision low
    positions = [
        {'x': 7500, 'y': 7500}, # River (center approx)
        {'x': 7600, 'y': 7400}, # River
        {'x': 7400, 'y': 7600}, # River
        {'x': 1000, 'y': 1000}, # Base
        {'x': 1100, 'y': 1100}  # Base
    ]
    detected = detect_patterns(positions, 600, vision_score=0.2)
    assert any(p['id'] == 'river_control_loss' for p in detected)
