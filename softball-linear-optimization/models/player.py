from dataclasses import dataclass


@dataclass
class Player:
    name: str
    email: str
    is_girl: int
    batting_skill: int
    attendance_0421: int
    attendance_0428: int
    attendance_0505: int
    attendance_0512: int
    attendance_0519: int
    attendance_0609: int
    possibilities: dict
