from fastapi.responses import JSONResponse
from app.storage import memory_store as db
from app.utils.responses import ok, err
from app.utils.security import valid_email, valid_password, hash_pw

COOKIE_KW = dict(
    key="sessionId",
    httponly=True,
    samesite="lax",
    secure=False,
    path="/",
)

def signup(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    password_confirm = payload.get("passwordConfirm")
    nickname = payload.get("nickname")
    profile_url = payload.get("profileImageUrl")

    if not email:
        err(400, "EMAIL_REQUIRED")
    if not password:
        err(400, "PASSWORD_REQUIRED")
    if password != password_confirm:
        err(400, "PASSWORD_CONFIRM_MISMATCH")
    if not nickname:
        err(400, "NICKNAME_REQUIRED")

    if not valid_email(email):
        err(400, "INVALID_EMAIL")
    if not valid_password(password):
        err(400, "INVALID_PASSWORD")
    if len(nickname) > 10:
        err(400, "INVALID_NICKNAME")

    if db.get_user_by_email(email):
        err(409, "EMAIL_ALREADY_EXISTS")
    if db.get_user_by_nickname(nickname):
        err(409, "NICKNAME_ALREADY_EXISTS")

    db.create_user(email, hash_pw(password), nickname, profile_url)
    return ok("SIGNUP_SUCCESS", None)

def login(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    if not email:
        err(400, "EMAIL_REQUIRED")
    if not password:
        err(400, "PASSWORD_REQUIRED")

    u = db.get_user_by_email(email)
    if not u or u["passwordHash"] != hash_pw(password):
        err(401, "UNAUTHORIZED")

    sid = db.create_session(u["userId"])

    res = JSONResponse(content=ok("LOGIN_SUCCESS", {
        "user": {
            "userId": u["userId"],
            "email": u["email"],
            "nickname": u["nickname"],
            "profileImageUrl": u.get("profileImageUrl"),
        }
    }))
    res.set_cookie(value=sid, **COOKIE_KW)
    return res

def logout(u_and_sid):
    _, sid = u_and_sid
    db.delete_session(sid)
    res = JSONResponse(content=ok("LOGOUT_SUCCESS", None))
    res.delete_cookie("sessionId", path="/")
    return res

def me(u):
    return ok("USER_RETRIEVED", {
        "userId": u["userId"],
        "email": u["email"],
        "nickname": u["nickname"],
        "profileImageUrl": u.get("profileImageUrl"),
    })

def email_availability(email: str):
    return ok("EMAIL_AVAILABLE", {"available": db.get_user_by_email(email) is None})

def nickname_availability(nickname: str):
    return ok("NICKNAME_AVAILABLE", {"available": db.get_user_by_nickname(nickname) is None})
