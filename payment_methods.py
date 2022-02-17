from enum import Enum, auto

class PaymentID(Enum):
    cash = auto()
    debit = auto()
    visa_1 = auto()
    visa_2 = auto()
    check = auto()
    paypal = auto()
    pc_optimum = auto()
    gift_card = auto()
