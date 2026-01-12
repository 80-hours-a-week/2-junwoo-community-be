from app.storage import memory_store as db
from app.utils.responses import ok, err
from app.utils.security import valid_email, valid_password, hash_pw

def signup(email: str, password: str, nickname: str, profile_url: str | None):
    if not valid_email(email):
        err(400, "INVALID_EMAIL")
    if not valid_password(password):
        err(400, "INVALID_PASSWORD")
    if not nickname:
        err(400, "NICKNAME_REQUIRED")
    if len(nickname) > 10:
        err(400, "INVALID_NICKNAME")

    if db.get_user_by_email(email):
        err(409, "EMAIL_ALREADY_EXISTS")
    if db.get_user_by_nickname(nickname):
        err(409, "NICKNAME_ALREADY_EXISTS")

    db.create_user(email, hash_pw(password), nickname, profile_url)
    return ok("SIGNUP_SUCCESS", None)

def login(email: str, password: str):
    if not email:
        err(400, "EMAIL_REQUIRED")
    if not password:
        err(400, "PASSWORD_REQUIRED")

    u = db.get_user_by_email(email)
    if not u or u.passwordHash != hash_pw(password):
        err(401, "UNAUTHORIZED")

    session_id = db.create_session(u.userId)
    return ok("LOGIN_SUCCESS", {
        "sessionId": session_id,  # 라우터에서 쿠키로 심고 body에서는 제거할 것
        "user": {
            "userId": u.userId,
            "email": u.email,
            "nickname": u.nickname,
            "profileImageUrl": u.profileImageUrl,
        }
    })

def logout(session_id: str):
    db.delete_session(session_id)
    return ok("LOGOUT_SUCCESS", None)

def me(u):
    return ok("USER_RETRIEVED", {
        "userId": u.userId,
        "email": u.email,
        "nickname": u.nickname,
        "profileImageUrl": u.profileImageUrl,
    })

def email_availability(email: str):
    return ok("EMAIL_AVAILABLE", {"available": db.get_user_by_email(email) is None})

def nickname_availability(nickname: str):
    return ok("NICKNAME_AVAILABLE", {"available": db.get_user_by_nickname(nickname) is None})
