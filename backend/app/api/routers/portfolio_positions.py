from fastapi import APIRouter, Depends, status
from app.schemas.portfolio_position import PortfolioPositionCreate
from app.core.database import SessionDep
from app.services.portfolio_positions import PortfolioPositionService
from app.api.deps import get_porfolio_position_service
router = APIRouter(prefix="/portfolio_positions", tags=["Portfolio Positions"])


@router.get("/{portfolio_position}")
async def get_portfolio_position(portfolio_position_id: int, service: PortfolioPositionService=Depends(get_porfolio_position_service)):
    return await service.get_by_id(
        portfolio_position_id=portfolio_position_id
    )

@router.get("/")
async def get_portfolio_positions(service: PortfolioPositionService=Depends(get_porfolio_position_service)):
    return await service.get_all()

@router.post("/")
async def create_portfolio_position(portfolio_position_schema: PortfolioPositionCreate, service: PortfolioPositionService=Depends(get_porfolio_position_service)):
    return await service.create(
        portfolio_position_schema=portfolio_position_schema
    )

@router.delete("/{portfolio_position}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(portfolio_position_id: int, service: PortfolioPositionService=Depends(get_porfolio_position_service)):
    await service.delete(
        portfolio_position_id=portfolio_position_id
    )
    return 
