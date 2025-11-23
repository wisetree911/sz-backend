from fastapi import APIRouter, status
from app.schemas.portfolio import PortfolioSchema
from app.core.database import SessionDep
from app.services.portfolios import PortfolioService
router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("/")
async def get_all(session: SessionDep):
    return await PortfolioService.get_all(session=session)

@router.get("/{portfolio_id}")
async def get_by_id(session: SessionDep, portfolio_id: int):
    return await PortfolioService.get_by_id(session=session, portfolio_id=portfolio_id)

@router.post("/{portfolio_id}")
async def create(session: SessionDep, portfolio_schema: PortfolioSchema):
    return await PortfolioService.create(session=session, portfolio_schema=portfolio_schema)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(session: SessionDep, portfolio_id: int):
    await PortfolioService.delete(session=session, portfolio_id=portfolio_id)
    return

