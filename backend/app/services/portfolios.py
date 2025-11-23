from app.repositories.portfolios import PortfolioRepository

from fastapi import HTTPException

class PortfolioService:
    @staticmethod
    async def get_all(session):
        return await PortfolioRepository.get_all(session=session)
    
    @staticmethod
    async def get_by_id(session, portfolio_id: int):
        portfolio = await PortfolioRepository.get_by_id(session=session, portfolio_id=portfolio_id)
        if portfolio is None:
            raise HTTPException(404, "SZ portfolio not found")
        return portfolio
    
    @staticmethod
    async def create(session, portfolio_schema):
        return await PortfolioRepository.create(
            session=session,
            user_id=portfolio_schema.user_id,
            name=portfolio_schema.name
        )
    
    @staticmethod
    async def delete(session, portfolio_id: int):
        portfolio = await PortfolioRepository.get_by_id(session=session, portfolio_id=portfolio_id)
        if portfolio is None:
            raise HTTPException(404, "SZ portfolio not found")
        
        await PortfolioRepository.delete(session=session, portfolio=portfolio)
    


# сделать получение всей инфы по всем портфелям (с дждоинами) юзера либо по конкретному портфелю (чисто айди портфеля)