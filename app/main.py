from fastapi import FastAPI
from app.routes.community import router as community_router

app = FastAPI(title="Junwoo Community API")

app.include_router(
    community_router,
    prefix="/community",
    tags=["Community"]
)
