from fastapi import APIRouter, status, Depends
from app.schemas.portfolio import PortfolioCreate, PortfolioResponse, PortfolioUpdateAdm, PortfolioUpdate
from app.services.portfolios import PortfolioService
from app.api.deps import get_porfolio_service
from app.api.deps import get_current_user
router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("/")
async def get_portfolios(current_user=Depends(get_current_user), service: PortfolioService=Depends(get_porfolio_service)) -> list[PortfolioResponse]:
    return await service.get_user_portfolios(user_id=current_user.id)

@router.get("/{portfolio_id}")
async def get_by_portfolio_id(portfolio_id:int, current_user=Depends(get_current_user), service: PortfolioService=Depends(get_porfolio_service)) -> PortfolioResponse:
    return await service.get_portfolio_for_user(portfolio_id=portfolio_id, user_id=current_user.id)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(portfolio_id: int, current_user=Depends(get_current_user), service: PortfolioService=Depends(get_porfolio_service)):
    await service.delete_portfolio_for_user(portfolio_id=portfolio_id, user_id=current_user.id)
    return None

@router.post("/")
async def create_portfolio_for_user(payload: PortfolioCreate, current_user=Depends(get_current_user), service: PortfolioService = Depends(get_porfolio_service)) -> PortfolioResponse:
    return await service.create_portfolio_for_user(payload=payload, user_id=current_user.id)

@router.patch("/{portfolio_id}")
async def update_portfolio_for_user(portfolio_id: int, payload: PortfolioUpdate, current_user=Depends(get_current_user), service: PortfolioService=Depends(get_porfolio_service)) -> PortfolioResponse:
    return await service.update_for_user(portfolio_id=portfolio_id, user_id=current_user.id, payload=payload)
