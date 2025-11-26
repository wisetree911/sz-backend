from backend.app.repositories.users import User
from backend.app.repositories.assets import Asset
from backend.app.repositories.portfolios import Portfolio
from backend.app.repositories.portfolio_positions import PortfolioPosition

# GET /users/{user_id}/portfolio/analytics
#     — обобщённая аналитика (вес позиций, total value)

# GET /users/{user_id}/portfolio/analytics/sectors
#     — данные по секторам

# GET /users/{user_id}/portfolio/analytics/dynamics
#     — данные для графика изменения стоимости

# GET /users/{user_id}/portfolio/analytics/positions
#     — взвешенные позиции

class AnalitycsService:
    @staticmethod 
    async def get_user_portfolios():
        ...
