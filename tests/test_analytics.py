import unittest
from core.analytics import get_distance, calculate_cohesion_score

class TestAnalytics(unittest.TestCase):
    def test_get_distance(self):
        # 3-4-5 Triangle
        p1 = {'x': 0, 'y': 0}
        p2 = {'x': 300, 'y': 400}
        self.assertEqual(get_distance(p1, p2), 500.0)
        
        # Same point
        self.assertEqual(get_distance(p1, p1), 0.0)

    def test_calculate_cohesion_score_compact(self):
        # Very compact team
        players = [
            {'x': 100, 'y': 100},
            {'x': 110, 'y': 110},
            {'x': 90, 'y': 90}
        ]
        score = calculate_cohesion_score(players)
        self.assertTrue(score > 90.0)

    def test_calculate_cohesion_score_split(self):
        # Very split team
        players = [
            {'x': 0, 'y': 0},
            {'x': 10000, 'y': 10000}
        ]
        score = calculate_cohesion_score(players)
        self.assertTrue(score < 20.0)

    def test_calculate_cohesion_score_empty(self):
        # Edge case: No players or 1 player
        self.assertEqual(calculate_cohesion_score([]), 100.0)
        self.assertEqual(calculate_cohesion_score([{'x': 0, 'y': 0}]), 100.0)

if __name__ == '__main__':
    unittest.main()
