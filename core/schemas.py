from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Position(BaseModel):
    x: float
    y: float

class Player(BaseModel):
    playerId: str
    team: str  # blue / red
    championId: Optional[int] = None
    position: Optional[Position] = None
    isAlive: bool = True
    currentHealth: Optional[int] = None
    maxHealth: Optional[int] = None

class GameFrame(BaseModel):
    timestamp: str
    matchTime: float
    players: List[Player]

class GameEvent(BaseModel):
    type: str
    timestamp: str
    payload: Dict[str, Any]

class SeriesData(BaseModel):
    seriesId: str
    frames: List[GameFrame] = Field(default_factory=list)
    events: List[GameEvent] = Field(default_factory=list)
