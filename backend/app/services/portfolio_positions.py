from shared.repositories.portfolio_position import PortfolioPositionRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class PortfolioPositionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PortfolioPositionRepository(session=session)

    async def get_all(self):
        return await self.repo.get_all()
    
    async def get_by_id(self, portfolio_position_id: int):
        portfolio_position = await self.repo.get_by_id(
            portflio_position_id=portfolio_position_id
        )
        if portfolio_position is None:
            raise HTTPException(404, "SZ portfolio position not found")
        return portfolio_position
    
    async def create(self, portfolio_position_schema):
        return await self.repo.create(
            portfolio_id=portfolio_position_schema.portfolio_id,
            asset_id=portfolio_position_schema.asset_id,
            quantity=portfolio_position_schema.quantity,
            avg_price=portfolio_position_schema.avg_price
        )
    
    async def delete(self, portfolio_position_id: int):
        portfolio_position = await self.repo.get_by_id(
            portflio_position_id=portfolio_position_id
            )
        if portfolio_position is None:
            raise HTTPException(404, "SZ portfolio position not found")
        
        await self.repo.delete(portfolio_position=portfolio_position)