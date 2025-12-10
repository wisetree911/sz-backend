from pydantic import BaseModel, Field
from datetime import datetime

class TradeBase(BaseModel):
    portfolio_id: int
    asset_id: int
    direction: str
    quantity: int
    price: float
    trade_time: datetime

class TradeCreate(TradeBase):
    pass

class TradeUpdate(TradeBase):
    portfolio_id: int | None  = None
    asset_id: int | None = None
    direction: str | None = None
    quantity: int | None = None
    price: int | None = None
    trade_time: int | None = None

class TradeResponse(TradeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 
    
