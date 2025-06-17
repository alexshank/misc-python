from dataclasses import dataclass


@dataclass
class Player:
    name: str
    email: str
    is_girl: int
    batting_skill: int
    attendance: dict  # Keys in "04/28" format
    possibilities: dict
