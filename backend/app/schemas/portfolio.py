from pydantic import BaseModel
from datetime import datetime

class PortfolioFields(BaseModel):
    name: str
    currency: str

class PortfolioCreatePublic(PortfolioFields):
    pass

class PortfolioUpdatePublic(BaseModel):
    name: str | None = None
    currency: str | None = None

class PortfolioCreateAdm(PortfolioFields):
    user_id: int

class PortfolioUpdateAdm(BaseModel):
    user_id: int | None = None
    name: str | None = None
    currency: str | None = None

class PortfolioResponseAdm(PortfolioFields):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True