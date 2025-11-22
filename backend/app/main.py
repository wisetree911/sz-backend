
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, DateTime, select
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text, ForeignKey, Numeric
DATABASE_URL = "postgresql+asyncpg://gagelang:toor@localhost:5432/portfolio_db"

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    future = True
)

async_session_maker = sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_session():
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    
class UserSchema(BaseModel):
    name: str
    age: int=Field(ge=0, le=130)

class PortfolioModel(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
class PortfolioSchema(BaseModel):
    user_id: int
    name: str

class PortfolioPositionModel(Base):
    __tablename__ = "portfolio_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE")
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    avg_price: Mapped[float] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

class PortfolioPositionScheme(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: int
    avg_price: int

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE")
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    direction: Mapped[str] = mapped_column(Text)  # buy / sell
    quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    price: Mapped[float] = mapped_column(Numeric, nullable=False)
    trade_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

app = FastAPI()


@app.post("/users/create")
async def add_users(user_schema: UserSchema, session: SessionDep):
    new_user = UserModel(
        name=user_schema.name,
        age=user_schema.age,
    )
    session.add(new_user)
    await session.commit()
    return "Aight"
    
@app.get("/users/list")
async def get_users(session: SessionDep):
    query = select(UserModel)
    result = await session.execute(query)
    return result.scalars().all()

@app.get("/users/{user_id}/portfolio", summary="Get concrete user portfolio")
async def get_user_portfolio(user_id: int, session: SessionDep):
    query = select(PortfolioModel).where(PortfolioModel.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

@app.post("/users/add_portfolio")
async def get_portfolios(portfolio_schema: PortfolioSchema, session: SessionDep):
    new_portfolio = PortfolioModel(
        user_id = portfolio_schema.user_id,
        name = portfolio_schema.name,
    )
    session.add(new_portfolio)
    await session.commit()
    return "Aight"

@app.get("/users/{portfolio_id}/positions", summary="Get concrete user concrete porfolio positions")
async def get_position(portfolio_id:int, session: SessionDep):
    query = select(PortfolioPositionModel).where(PortfolioPositionModel.portfolio_id == portfolio_id)
    result = await session.execute(query)
    return result.scalars().all()


