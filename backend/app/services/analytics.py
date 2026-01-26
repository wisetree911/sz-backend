from datetime import datetime, timedelta
from decimal import Decimal

from app.analytics.analytics_calc import (
    build_dynamics_positions,
    build_only_buy_positions,
    build_sector_positions,
    build_time_series,
    calc_cost_basis,
    calc_market_value,
    calc_unrealized_pnl,
    calc_unrealized_return_pct,
)
from app.analytics.models import PortfolioPositionPrepared, SectorPosition, TradeDTO
from app.schemas.analytics import (
    PortfolioDynamicsResponse,
    PortfolioPrice,
    PortfolioSnapshotResponse,
    SectorDistributionPosition,
    SectorDistributionResponse,
    TopPosition,
)
from fastapi import HTTPException
from shared.models.portfolio import Portfolio
from shared.repositories.asset import AssetRepository
from shared.repositories.asset_price import AssetPriceRepository
from shared.repositories.portfolio import PortfolioRepository
from shared.repositories.trade import TradeRepository
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession


# убрать всю аналитику отсюлаёёда
class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.asset_price_repo = AssetPriceRepository(session=session)
        self.portfolio_repo = PortfolioRepository(session=session)
        self.asset_repo = AssetRepository(session=session)
        self.trade_repo = TradeRepository(session=session)

    async def portfolio_snapshot(self, portfolio_id: int) -> PortfolioSnapshotResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(404, 'SZ portfolio not found')
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        if not portfolio_trades:
            return PortfolioSnapshotResponse.empty(portfolio)
        asset_ids = {trade.asset_id for trade in portfolio_trades}
        asset_market_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        trade_dtos = [TradeDTO.from_orm(trade) for trade in portfolio_trades]

        assets = await self.asset_repo.get_assets_by_ids(asset_ids)
        portfolio_positions: list[PortfolioPositionPrepared] = build_only_buy_positions(
            trades=trade_dtos, current_prices=asset_market_prices, assets=assets
        )
        cost_basis = calc_cost_basis(asset_positive_positons=portfolio_positions)
        unrealized_pnl = calc_unrealized_pnl(asset_positive_positons=portfolio_positions)
        market_price = calc_market_value(asset_positive_positons=portfolio_positions)

        top_positions = [
            TopPosition(
                asset_id=pos.asset_id,
                ticker=pos.ticker,
                full_name=pos.name,
                quantity=pos.quantity,
                avg_buy_price=pos.mid_price,
                asset_market_price=pos.asset_market_price,
                market_value=pos.market_price,
                unrealized_pnl=pos.unrealized_pnl,
                unrealized_return_pct=pos.unrealized_return_pct,
                weight_pct=pos.market_price / market_price * 100,
            )
            for pos in sorted(
                portfolio_positions,
                key=lambda pos: pos.market_price / market_price * 100,
                reverse=True,
            )[:5]
        ]

        return PortfolioSnapshotResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=market_price,
            unrealized_pnl=unrealized_pnl,
            unrealized_return_pct=calc_unrealized_return_pct(
                unrealized_pnl=unrealized_pnl, cost_basis=cost_basis
            ),
            cost_basis=cost_basis,
            currency=portfolio.currency,
            positions_count=len(portfolio_positions),
            top_positions=top_positions,
        )

    async def portfolio_snapshot_for_user(
        self, portfolio_id: int, user_id: int
    ) -> PortfolioSnapshotResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(404, 'SZ portfolio not found')
        if portfolio.user_id != user_id:
            raise HTTPException(404, 'SZ portfolio not found')
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        if not portfolio_trades:
            return PortfolioSnapshotResponse.empty(portfolio)
        asset_ids = {trade.asset_id for trade in portfolio_trades}
        asset_market_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        trade_dtos = [TradeDTO.from_orm(trade) for trade in portfolio_trades]

        assets = await self.asset_repo.get_assets_by_ids(asset_ids)
        portfolio_positions: list[PortfolioPositionPrepared] = build_only_buy_positions(
            trades=trade_dtos, current_prices=asset_market_prices, assets=assets
        )
        cost_basis = calc_cost_basis(asset_positive_positons=portfolio_positions)
        unrealized_pnl = calc_unrealized_pnl(asset_positive_positons=portfolio_positions)
        market_price = calc_market_value(asset_positive_positons=portfolio_positions)

        top_positions = [
            TopPosition(
                asset_id=pos.asset_id,
                ticker=pos.ticker,
                full_name=pos.name,
                quantity=pos.quantity,
                avg_buy_price=pos.mid_price,
                asset_market_price=pos.asset_market_price,
                market_value=pos.market_price,
                unrealized_pnl=pos.unrealized_pnl,
                unrealized_return_pct=pos.unrealized_return_pct,
                weight_pct=pos.market_price / market_price * 100,
            )
            for pos in sorted(
                portfolio_positions,
                key=lambda pos: pos.market_price / market_price * 100,
                reverse=True,
            )[:5]
        ]

        return PortfolioSnapshotResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=market_price,
            unrealized_pnl=unrealized_pnl,
            unrealized_return_pct=calc_unrealized_return_pct(
                unrealized_pnl=unrealized_pnl, cost_basis=cost_basis
            ),
            cost_basis=cost_basis,
            currency=portfolio.currency,
            positions_count=len(portfolio_positions),
            top_positions=top_positions,
        )

    async def sector_distribution(self, portfolio_id: int) -> SectorDistributionResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(404, 'SZ portfolio not found')
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        if not portfolio_trades:
            return SectorDistributionResponse.empty(portfolio)
        asset_ids = {trade.asset_id for trade in portfolio_trades}
        market_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        assets = await self.asset_repo.get_assets_by_ids(asset_ids)
        trade_dtos = [TradeDTO.from_orm(trade) for trade in portfolio_trades]
        sector_positions: list[SectorPosition] = build_sector_positions(
            trades=trade_dtos, current_prices=market_prices, assets=assets
        )
        portfolio_market_value = sum(pos.market_value for pos in sector_positions)

        secs: list[SectorDistributionPosition] = [
            SectorDistributionPosition(
                sector=pos.sector,
                market_value=pos.market_value,
                weight_percent=pos.market_value / portfolio_market_value * 100,
            )
            for pos in sector_positions
        ]

        return SectorDistributionResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=portfolio_market_value,
            currency=portfolio.currency,
            sectors=secs,
        )

    async def sector_distribution_for_user(
        self, portfolio_id: int, user_id: int
    ) -> SectorDistributionResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(404, 'SZ portfolio not found')
        if portfolio.user_id != user_id:
            raise HTTPException(404, 'SZ portfolio not found')
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        if not portfolio_trades:
            return SectorDistributionResponse.empty(portfolio)
        asset_ids = {trade.asset_id for trade in portfolio_trades}
        market_prices = await self.asset_price_repo.get_prices_dict_by_ids(asset_ids)
        assets = await self.asset_repo.get_assets_by_ids(asset_ids)
        trade_dtos = [TradeDTO.from_orm(trade) for trade in portfolio_trades]
        sector_positions: list[SectorPosition] = build_sector_positions(
            trades=trade_dtos, current_prices=market_prices, assets=assets
        )
        portfolio_market_value = sum(pos.market_value for pos in sector_positions)

        secs: list[SectorDistributionPosition] = [
            SectorDistributionPosition(
                sector=pos.sector,
                market_value=pos.market_value,
                weight_percent=pos.market_value / portfolio_market_value * 100,
            )
            for pos in sector_positions
        ]

        return SectorDistributionResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=portfolio_market_value,
            currency=portfolio.currency,
            sectors=secs,
        )

    async def portfolio_dynamics_for_24h(self, portfolio_id: int) -> PortfolioDynamicsResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        dynamic_positions = build_dynamics_positions(trades=portfolio_trades)
        asset_ids = [pos.asset_id for pos in dynamic_positions]
        timestamp_now = datetime.utcnow()
        asset_prices_history = await self.asset_price_repo.get_prices_since(
            ids=asset_ids, since=timestamp_now - timedelta(days=1)
        )

        time_series = build_time_series(
            timestamp_now=timestamp_now,
            asset_prices=asset_prices_history,
            dynamic_positions=dynamic_positions,
        )
        prices = [
            PortfolioPrice(timestamp=serie.timestamp, total_value=serie.price)
            for serie in time_series
        ]
        return PortfolioDynamicsResponse(
            portfolio_id=portfolio.id, name=portfolio.name, data=prices
        )

    async def portfolio_dynamics_for_24h_for_user(
        self, portfolio_id: int, user_id: int
    ) -> PortfolioDynamicsResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise HTTPException(404, 'SZ portfolio not found')
        if portfolio.user_id != user_id:
            raise HTTPException(404, 'SZ portfolio not found')
        portfolio_trades = await self.trade_repo.get_trades_by_portfolio_id(portfolio_id)
        dynamic_positions = build_dynamics_positions(trades=portfolio_trades)
        asset_ids = [pos.asset_id for pos in dynamic_positions]
        timestamp_now = datetime.utcnow()
        asset_prices_history = await self.asset_price_repo.get_prices_since(
            ids=asset_ids, since=timestamp_now - timedelta(days=1)
        )

        time_series = build_time_series(
            timestamp_now=timestamp_now,
            asset_prices=asset_prices_history,
            dynamic_positions=dynamic_positions,
        )
        prices = [
            PortfolioPrice(timestamp=serie.timestamp, total_value=serie.price)
            for serie in time_series
        ]
        return PortfolioDynamicsResponse(
            portfolio_id=portfolio.id, name=portfolio.name, data=prices
        )

    async def portfolio_snapshot_v2(self, portfolio_id: int) -> PortfolioSnapshotResponse:
        row = await self.session.execute(
            select(Portfolio.id, Portfolio.name, Portfolio.currency).where(
                Portfolio.id == portfolio_id
            )
        )
        portfolio = row.one_or_none()
        if portfolio is None:
            raise HTTPException(404, 'SZ portfolio not found')

        totals_sql = text("""
            WITH pos AS (
                SELECT
                    t.asset_id,
                    SUM(t.quantity) AS quantity,
                    SUM(t.quantity * t.price) AS cost_basis
                FROM trades t
                WHERE t.portfolio_id = :portfolio_id
                  AND t.direction = 'buy'
                GROUP BY t.asset_id
            ),
            latest_price AS (
                SELECT DISTINCT ON (ap.asset_id)
                    ap.asset_id,
                    ap.price AS asset_market_price,
                    ap.timestamp AS as_of
                FROM asset_prices ap
                JOIN pos ON pos.asset_id = ap.asset_id
                ORDER BY ap.asset_id, ap.timestamp DESC
            ),
            enriched AS (
                SELECT
                    pos.asset_id,
                    a.ticker,
                    a.full_name,
                    pos.quantity,
                    pos.cost_basis,
                    (pos.cost_basis / NULLIF(pos.quantity, 0)) AS avg_buy_price,
                    COALESCE(lp.asset_market_price, 0) AS asset_market_price,
                    (pos.quantity * COALESCE(lp.asset_market_price, 0)) AS market_value,
                    ((pos.quantity * COALESCE(lp.asset_market_price, 0)) - pos.cost_basis) AS unrealized_pnl,
                    (
                        ((pos.quantity * COALESCE(lp.asset_market_price, 0)) - pos.cost_basis)
                        / NULLIF(pos.cost_basis, 0) * 100
                    ) AS unrealized_return_pct
                FROM pos
                JOIN assets a ON a.id = pos.asset_id
                LEFT JOIN latest_price lp ON lp.asset_id = pos.asset_id
            )
            SELECT
                COALESCE(SUM(enriched.market_value), 0) AS market_value,
                COALESCE(SUM(enriched.unrealized_pnl), 0) AS unrealized_pnl,
                COALESCE(SUM(enriched.cost_basis), 0) AS cost_basis,
                COUNT(*) AS positions_count
            FROM enriched;
        """)

        totals_row = (
            (await self.session.execute(totals_sql, {'portfolio_id': portfolio_id}))
            .mappings()
            .one()
        )

        if int(totals_row['positions_count']) == 0:
            return PortfolioSnapshotResponse.empty(
                Portfolio(id=portfolio.id, name=portfolio.name, currency=portfolio.currency)
            )

        top5_sql = text("""
            WITH pos AS (
                SELECT
                    t.asset_id,
                    SUM(t.quantity) AS quantity,
                    SUM(t.quantity * t.price) AS cost_basis
                FROM trades t
                WHERE t.portfolio_id = :portfolio_id
                  AND t.direction = 'buy'
                GROUP BY t.asset_id
            ),
            latest_price AS (
                SELECT DISTINCT ON (ap.asset_id)
                    ap.asset_id,
                    ap.price AS asset_market_price,
                    ap.timestamp AS as_of
                FROM asset_prices ap
                JOIN pos ON pos.asset_id = ap.asset_id
                ORDER BY ap.asset_id, ap.timestamp DESC
            ),
            enriched AS (
                SELECT
                    pos.asset_id,
                    a.ticker,
                    a.full_name,
                    pos.quantity,
                    pos.cost_basis,
                    (pos.cost_basis / NULLIF(pos.quantity, 0)) AS avg_buy_price,
                    COALESCE(lp.asset_market_price, 0) AS asset_market_price,
                    (pos.quantity * COALESCE(lp.asset_market_price, 0)) AS market_value,
                    ((pos.quantity * COALESCE(lp.asset_market_price, 0)) - pos.cost_basis) AS unrealized_pnl,
                    (
                        ((pos.quantity * COALESCE(lp.asset_market_price, 0)) - pos.cost_basis)
                        / NULLIF(pos.cost_basis, 0) * 100
                    ) AS unrealized_return_pct
                FROM pos
                JOIN assets a ON a.id = pos.asset_id
                LEFT JOIN latest_price lp ON lp.asset_id = pos.asset_id
            )
            SELECT
                e.asset_id,
                e.ticker,
                e.full_name,
                e.quantity,
                e.avg_buy_price,
                e.asset_market_price,
                e.market_value,
                e.unrealized_pnl,
                e.unrealized_return_pct,
                (e.market_value / NULLIF(SUM(e.market_value) OVER (), 0) * 100) AS weight_pct
            FROM enriched e
            ORDER BY weight_pct DESC NULLS LAST
            LIMIT 5;
        """)

        top_rows = (
            (await self.session.execute(top5_sql, {'portfolio_id': portfolio_id})).mappings().all()
        )

        market_value = Decimal(totals_row['market_value'])
        unrealized_pnl = Decimal(totals_row['unrealized_pnl'])
        cost_basis = Decimal(totals_row['cost_basis'])

        unreal_total_ret = (
            (unrealized_pnl / cost_basis * Decimal(100)) if cost_basis else Decimal(0)
        )

        return PortfolioSnapshotResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_return_pct=unreal_total_ret,
            cost_basis=cost_basis,
            currency=portfolio.currency,
            positions_count=int(totals_row['positions_count']),
            top_positions=[
                TopPosition(
                    asset_id=r['asset_id'],
                    ticker=r['ticker'],
                    full_name=r['full_name'],
                    quantity=Decimal(r['quantity']) if r['quantity'] is not None else Decimal(0),
                    avg_buy_price=Decimal(r['avg_buy_price'])
                    if r['avg_buy_price'] is not None
                    else Decimal(0),
                    asset_market_price=Decimal(r['asset_market_price'])
                    if r['asset_market_price'] is not None
                    else Decimal(0),
                    market_value=Decimal(r['market_value'])
                    if r['market_value'] is not None
                    else Decimal(0),
                    unrealized_pnl=Decimal(r['unrealized_pnl'])
                    if r['unrealized_pnl'] is not None
                    else Decimal(0),
                    unrealized_return_pct=Decimal(r['unrealized_return_pct'])
                    if r['unrealized_return_pct'] is not None
                    else Decimal(0),
                    weight_pct=Decimal(r['weight_pct'])
                    if r['weight_pct'] is not None
                    else Decimal(0),
                )
                for r in top_rows
            ],
        )
