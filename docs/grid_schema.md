# GRID Data Schema Documentation

## Overview
This document describes the structure of the GRID JSONL data used for the Macro Health Monitor.

## Root Structure
- `data`: Root container
    - `seriesState`: Container for the match series
        - `id`: Unique identifier for the series
        - `games`: List of game objects

## Game Object
- `teams`: List of 2 team objects (Blue, Red)
- `events`: List of match events

## Team Object
- `players`: List of 5 player objects

## Player Object
- `id`: Player identifier
- `name`: Player name
- `position`: Current coordinate object
    - `x`: X-coordinate (0 to ~15000)
    - `y`: Y-coordinate (0 to ~15000)
- `alive`: Boolean status (default: true)

## Spatial Analytics Logic
The `x` and `y` coordinates are used to calculate:
1. **Team Cohesion:** Average distance from the team centroid.
2. **Lonely Carry Index (LCI):** Distance of key roles from allies vs distance to enemies.
3. **Teamfight Proximity:** Density of players from both teams in a 2000-unit radius.
