from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.index import register_routers
from app.utils.responses import ok

app = FastAPI(title="Community API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return ok("OK", None)

# ✅ 라우터 등록은 index에서 한 번에
register_routers(app)

