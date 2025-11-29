from sqlalchemy import select
from shared.models.portfolio_position import PortfolioPosition
from sqlalchemy.ext.asyncio import AsyncSession

class PortfolioPositionRepository:
    def __init__(self, session: AsyncSession):
        self.session=session

    async def get_by_id(self, portflio_position_id: int):
        query = select(PortfolioPosition).where(PortfolioPosition.id == portflio_position_id)
        result = await self.session.execute(query)
        portflio_position = result.scalar_one_or_none()
        return portflio_position
    
    async def get_all(self):
        query = select(PortfolioPosition)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    
    
    async def create(self, portfolio_id: int, asset_id: int, quantity: int, avg_price: int):
        new_portflio_position = PortfolioPosition(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            quantity=quantity,
            avg_price=avg_price
        )
        self.session.add(new_portflio_position)
        await self.session.commit()
        await self.session.refresh(new_portflio_position)
        return new_portflio_position
    
    async def delete(self, portfolio_position: PortfolioPosition):
        await self.session.delete(portfolio_position)
        await self.session.commit()

    async def get_by_portfolio_id(self, portfolio_id):
        query = select(PortfolioPosition).where(PortfolioPosition.portfolio_id == portfolio_id)
        portfolio_positions = await self.session.execute(query)
        return portfolio_positions.scalars().all()
