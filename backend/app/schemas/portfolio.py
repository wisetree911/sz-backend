from pydantic import BaseModel
from datetime import datetime


class PortfolioCreate(BaseModel):
    name: str
    currency: str

class PortfolioUpdate(BaseModel):
    name: str | None = None
    currency: str | None = None

class PortfolioBase(BaseModel):
    user_id: int
    name: str
    currency: str

class PortfolioCreateAdm(PortfolioBase):
    pass



class PortfolioUpdateAdm(PortfolioBase):
    user_id: int | None = None
    name: str | None = None
    currency: str | None = None
    
class PortfolioResponse(PortfolioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

