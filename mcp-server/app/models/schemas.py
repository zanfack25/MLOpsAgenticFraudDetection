from pydantic import BaseModel

class TransactionInput(BaseModel):
    ip: str
    device_id: str
    location: str
    time: str
    amount: float
    merchant_id: str
    receiver_bank: str
    metadata: str
