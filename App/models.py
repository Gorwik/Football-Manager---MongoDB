from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
from enum import Enum


Positions = Enum(
    "Positions",
    [
        "RW",
        "LCM",
        "LS",
        "LCB",
        "ST",
        "GK",
        "RS",
        "CDM",
        "SUB",
        "RCB",
        "LB",
        "LDM",
        "CAM",
        "RAM",
        "LW",
        "LAM",
        "CM",
        "RM",
        "LM",
        "RES",
        "RB",
        "RDM",
        "RCM",
        "LWB",
        "LF",
        "CB",
        "RWB",
        "RF",
        "CF",
    ],
)
Foot = Enum("Foot", ["LEFT", "RIGHT"])


class PlayersSimpliefied(BaseModel):
    id: object
    first_name: str
    last_name: Optional[str] = None
    date_of_birth: datetime
    country: str
    overall: Optional[int] = None


class PlayerStats(BaseModel):
    season: int
    club_id: object
    club_name: str
    goals: Optional[int] = None
    assists: Optional[int] = None
    min_on_a_pitch: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    kit_number: Optional[int] = None


class PlayerSpecific(PlayersSimpliefied):
    height: Optional[int] = None
    weight: Optional[int] = None
    pref_pos: Optional[Positions] = None
    value: Optional[int] = None
    wage: Optional[int] = None
    pref_foot: Optional[Foot] = None
    age: Optional[int] = None
    club_id: Optional[object] = None
    club_name: Optional[str] = None
    stats: Optional[list[PlayerStats]] = None


class Players(BaseModel):
    head: list[Union[object, str]]
    substitute: Optional[list[Union[object, str]]] = None


class ClubStats(BaseModel):
    season: int
    league: object
    points: int
    coach: Union[object, str]
    won_titles: Optional[int] = None
    players: Players


class Club(BaseModel):
    id: object
    name: str
    country: str
    seasons: Optional[ClubStats] = None
