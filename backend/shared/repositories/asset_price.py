from sqlalchemy import select
from shared.models.asset_price import AssetPrice
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

class AssetPriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, asset_id: int):
        query = select(AssetPrice).where(AssetPrice.asset_id == asset_id)
        result = await self.session.execute(query)
        asserts = result.scalars().all()
        return asserts
    
    @staticmethod
    async def get_all(self):
        query = select(AssetPrice)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create(self,
            asset_id,
            price,
            currency,
            source):
        new_price = AssetPrice(
            asset_id=asset_id,
            price=price,
            currency=currency,
            source=source
        )
        self.session.add(new_price)
        await self.session.commit()
        await self.session.refresh(new_price)
        return new_price
    
    @staticmethod
    async def get_prices_since(self, ids: list[int], since: datetime):
        if not ids: return []
        query = (select(AssetPrice).where(AssetPrice.asset_id.in_(ids), AssetPrice.timestamp >= since))
        prices = await self.session.execute(query)
        return prices.scalars().all()
    