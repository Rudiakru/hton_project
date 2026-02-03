import asyncio
import json


def test_process_match_data_caches_by_filename():
    from backend import main

    main.parsing_cache.clear()

    frame_1 = {
        "data": {
            "seriesState": {
                "id": "S1",
                "games": [
                    {
                        "teams": []
                    }
                ]
            }
        }
    }

    frame_2 = {
        "data": {
            "seriesState": {
                "id": "S2",
                "games": [
                    {
                        "teams": []
                    }
                ]
            }
        }
    }

    content_1 = (json.dumps(frame_1) + "\n").encode("utf-8")
    content_2 = (json.dumps(frame_2) + "\n").encode("utf-8")

    result_1 = asyncio.run(main.process_match_data(content_1, filename="match.jsonl"))
    result_2 = asyncio.run(main.process_match_data(content_2, filename="match.jsonl"))

    assert result_1["series_id"] == "S1"
    assert result_2 is result_1
    assert main.parsing_cache["match.jsonl"] is result_1
