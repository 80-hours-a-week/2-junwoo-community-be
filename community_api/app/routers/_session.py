from fastapi import Cookie
from app.utils.responses import err
from app.storage import memory_store as db

def require_user(sessionId: str | None = Cookie(None)):
    if not sessionId:
        err(401, "UNAUTHORIZED")
    u = db.session_user(sessionId)
    if not u:
        err(401, "UNAUTHORIZED")
    return u, sessionId
