from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import health, journeys, locations
from app.seed import seed_reference_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_reference_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router)
app.include_router(journeys.router)
app.include_router(locations.router)
