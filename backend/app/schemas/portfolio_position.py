from pydantic import BaseModel

class PortfolioPositionBase(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: int
    avg_price: int

class PortfolioPositionCreate(PortfolioPositionBase):
    pass

