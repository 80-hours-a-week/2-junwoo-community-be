from fastapi import Cookie
from app.storage import memory_store as db
from app.utils.responses import err

def require_user(sessionId: str | None = Cookie(None)):
    if not sessionId:
        err(401, "UNAUTHORIZED")
    u = db.session_user(sessionId)
    if not u:
        err(401, "UNAUTHORIZED")
    return u

def require_user_with_sid(sessionId: str | None = Cookie(None)):
    if not sessionId:
        err(401, "UNAUTHORIZED")
    u = db.session_user(sessionId)
    if not u:
        err(401, "UNAUTHORIZED")
    return u, sessionId

