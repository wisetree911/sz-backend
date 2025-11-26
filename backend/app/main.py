
from fastapi import FastAPI
from backend.app.routers import users, assets, portfolios, portfolio_positions, trades, analytics
app = FastAPI()
app.include_router(users.router)
app.include_router(assets.router)
app.include_router(portfolios.router)
app.include_router(portfolio_positions.router)
app.include_router(trades.router)
app.include_router(analytics.router)