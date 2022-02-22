from dataclasses import dataclass


@dataclass
class PaymentType:
    id: int
    name: str
    description: str
