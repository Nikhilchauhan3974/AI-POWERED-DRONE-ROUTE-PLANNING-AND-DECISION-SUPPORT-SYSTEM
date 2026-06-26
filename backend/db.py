from datetime import datetime
import json
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.config import settings

# Create async engine and sessionmaker
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_lat = Column(Float, nullable=False)
    source_lon = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)
    algorithm = Column(String, nullable=False)
    weather = Column(String, nullable=False)
    wind_speed = Column(Float, default=0.0)
    wind_direction = Column(Float, default=0.0)
    distance = Column(Float, nullable=False)  # in meters
    travel_time = Column(Float, nullable=False)  # in seconds
    battery_consumed = Column(Float, nullable=False)  # percentage
    risk_score = Column(Float, nullable=False)  # 0 to 1
    path_coords = Column(Text, nullable=False)  # JSON serialized list of [lat, lon]
    created_at = Column(DateTime, default=datetime.utcnow)

class Obstacle(Base):
    __tablename__ = "obstacles"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)  # in meters
    risk_level = Column(Float, nullable=False)  # 0 to 1
    cost = Column(Float, nullable=False)  # Cost multiplier
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(Integer, primary_key=True, index=True)
    algorithm = Column(String, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    nodes_visited = Column(Integer, nullable=False)
    path_length = Column(Float, nullable=False)  # total cell distance or meters
    cost = Column(Float, nullable=False)
    battery_consumed = Column(Float, nullable=False)  # percentage
    risk_score = Column(Float, nullable=False)  # 0 to 1
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
