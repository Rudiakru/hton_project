import math

# GRID coordinates approximate for Summoner's Rift
# (0,0) is bottom left, (15000, 15000) is top right
BARON_POS = {'x': 5000, 'y': 10000}
DRAGON_POS = {'x': 10000, 'y': 5000}

def get_distance(p1, p2):
    return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)

def is_in_lane(pos, lane):
    x, y = pos['x'], pos['y']
    if lane == "top":
        return x < 4000 and y > 6000
    if lane == "mid":
        # Mid is roughly diagonal from (0,0) to (15000, 15000)
        return abs(x - y) < 2000
    if lane == "bot":
        return x > 6000 and y < 4000
    if lane == "river":
        # River is roughly the other diagonal
        return abs(x + y - 15000) < 2000
    return False

def detect_patterns(player_positions, game_time_seconds, vision_score=1.0):
    detected = []
    
    # 1. Baron Setup
    # Assume Baron spawns at 20:00 (1200s) and every 6 mins after if killed.
    # For demo, let's just check proximity to Baron pit if game_time > 1200
    if game_time_seconds > 1170: # 30s before or after 20:00
        avg_dist_to_baron = sum(get_distance(p, BARON_POS) for p in player_positions) / len(player_positions) if player_positions else 9999
        if avg_dist_to_baron < 3000:
            detected.append({
                "id": "baron_setup",
                "label": "Baron Setup",
                "win_rate": 0.73,
                "description": "Team is positioning around Baron pit for objective control."
            })

    # 2. Split Push 1-4
    top_count = sum(1 for p in player_positions if is_in_lane(p, "top"))
    mid_count = sum(1 for p in player_positions if is_in_lane(p, "mid"))
    bot_count = sum(1 for p in player_positions if is_in_lane(p, "bot"))
    
    if (top_count == 1 and (mid_count >= 4 or bot_count >= 4)) or (bot_count == 1 and (mid_count >= 4 or top_count >= 4)):
        detected.append({
            "id": "split_push_1_4",
            "label": "Split Push 1-4",
            "win_rate": 0.61,
            "description": "One player is drawing pressure while the rest of the team groups."
        })

    # 3. River Control Loss
    river_count = sum(1 for p in player_positions if is_in_lane(p, "river"))
    if vision_score < 0.4 and river_count >= 3:
        detected.append({
            "id": "river_control_loss",
            "label": "River Control Loss",
            "win_rate": 0.42,
            "description": "Team is entering river with low vision, high risk of ambush."
        })

    return detected
