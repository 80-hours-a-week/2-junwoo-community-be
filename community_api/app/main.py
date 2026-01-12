from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.routers.auth_router import router as auth_router
from app.routers.users_router import router as users_router
from app.routers.posts_router import router as posts_router
from app.routers.public_router import router as public_router

app = FastAPI(title="아무 말 대잔치 API", version="0.1.0")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # detail에 {"code": "...", "data": None} 넣는 방식으로 통일
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    # fallback
    return JSONResponse(status_code=exc.status_code, content={"code": "BAD_REQUEST", "data": None})

@app.get("/health")
def health():
    return {"code": "OK", "data": None}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)
app.include_router(public_router)
