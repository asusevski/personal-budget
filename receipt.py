from dataclasses import dataclass


@dataclass
class Receipt:
    id: int
    total: float
    date: str
    location: str
        