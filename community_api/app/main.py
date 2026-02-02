from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.routers.index import register_routers
from app.utils.responses import success_response

app = FastAPI(title="Community API")

# ✅ 쿠키 기반 세션이면 "*" 절대 금지
FRONT_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONT_ORIGINS,   # ✅ 정확한 origin만 허용
    allow_credentials=True,        # ✅ 쿠키 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"code": "BAD_REQUEST", "message": "Bad request"},
    )

@app.get("/health")
def health():
    return success_response("OK", None)

register_routers(app)
