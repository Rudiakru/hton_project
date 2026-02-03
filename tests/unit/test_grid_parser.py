import pytest
import json
from backend.parsers.grid_parser import load_grid_data, extract_player_positions

def test_load_grid_data_not_found():
    with pytest.raises(FileNotFoundError):
        load_grid_data("non_existent.json")

def test_load_grid_data_invalid_format(tmp_path):
    d = tmp_path / "invalid.json"
    d.write_text(json.dumps({"wrong": "format"}))
    with pytest.raises(ValueError, match="'data.seriesState' fehlt"):
        load_grid_data(str(d))

def test_extract_player_positions():
    mock_game = {
        "teams": [
            {
                "players": [
                    {"id": "1", "name": "Player1", "position": {"x": 100, "y": 200}, "alive": True},
                    {"id": "2", "name": "Player2", "position": {"x": 300, "y": 400}, "alive": False}
                ]
            },
            {
                "players": [
                    {"id": "3", "name": "Player3", "position": {"x": 500, "y": 600}}
                ]
            }
        ]
    }
    positions = extract_player_positions(mock_game)
    assert len(positions) == 2
    assert len(positions[0]) == 2
    assert positions[0][0]["name"] == "Player1"
    assert not positions[0][1]["alive"]
    assert positions[1][0]["x"] == 500.0

def test_extract_player_positions_missing_coords():
    mock_game = {
        "teams": [
            {
                "players": [
                    {"id": "1", "name": "NoPos", "position": None}
                ]
            }
        ]
    }
    positions = extract_player_positions(mock_game)
    assert len(positions[0]) == 0
