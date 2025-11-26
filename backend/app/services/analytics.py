from sqlalchemy import select, func
from datetime import datetime, timedelta
from backend.app.repositories.asset_prices import AssetPriceRepository
from backend.app.repositories.portfolios import PortfolioRepository
from backend.app.repositories.portfolio_positions import PortfolioPositionRepository
class AnalyticsService:

    @staticmethod
    async def portfolio_dynamics(session, user_id: int):
        portfolios = await PortfolioRepository.get_by_user_id(session=session, user_id=user_id)

        portfolios_list = []
        for portfolio in portfolios:
            positions = await PortfolioPositionRepository.get_by_portfolio_id(session=session, portfolio_id=portfolio.id)

            asset_ids = [p.asset_id for p in positions]
            pos_dict = {p.asset_id: p.quantity for p in positions}

            since = datetime.utcnow() - timedelta(hours=24)
            prices = await AssetPriceRepository.get_prices_since(session=session, ids=asset_ids, since=since)
            time_map = {}

            for price in prices:
                ts = price.timestamp
                asset_id = price.asset_id

                if ts not in time_map:
                    time_map[ts] = 0

                time_map[ts] += price.price * pos_dict[asset_id]
            portfolio_dict = {}
            portfolio_dict["name"] = portfolio.name
            portfolio_dict["id"] = portfolio.id
            
            ls = []
            ls = [
                    {
                        "timestamp": ts.isoformat(),
                        "value": float(val)
                    }
                    for ts, val in sorted(time_map.items(), key=lambda x: x[0])
                ]
            
            portfolio_dict["data"] = ls
            portfolios_list.append(portfolio_dict)
            

        return portfolios_list


