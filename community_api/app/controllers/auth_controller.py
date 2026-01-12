from fastapi import UploadFile
from app.utils.responses import ok, err
from app.utils.security import hash_pw, validate_email, validate_password_rule, validate_nickname
from app.storage import memory_store as db

def signup(email: str, password: str, nickname: str, profile: UploadFile | None):
    if not email:
        err(400, "EMAIL_REQUIRED")
    if not validate_email(email):
        err(400, "INVALID_EMAIL")
    if not password:
        err(400, "PASSWORD_REQUIRED")
    if not validate_password_rule(password):
        err(400, "INVALID_PASSWORD")
    if not validate_nickname(nickname):
        err(400, "INVALID_NICKNAME")

    if db.get_user_by_email(email):
        err(409, "EMAIL_ALREADY_EXISTS")
    if db.get_user_by_nickname(nickname):
        err(409, "NICKNAME_ALREADY_EXISTS")

    profile_url = None
    if profile is not None:
        raw = profile.file.read()
        if raw:
            fid = db.new_id()
            db.files[fid] = raw
            db.file_mimes[fid] = profile.content_type or "application/octet-stream"
            # 엑셀 예시 경로: /public/image/profile/xxx.jpg
            profile_url = f"/public/image/profile/{fid}"

    db.create_user(email, hash_pw(password), nickname, profile_url)
    return ok("SIGNUP_SUCCESS", None)

def login(email: str, password: str):
    if not email:
        err(400, "EMAIL_REQUIRED")
    if not password:
        err(400, "PASSWORD_REQUIRED")

    u = db.get_user_by_email(email)
    if not u:
        err(401, "UNAUTHORIZED")

    if u.passwordHash != hash_pw(password):
        err(401, "UNAUTHORIZED")

    token = db.create_session(u.userId)

    return ok("LOGIN_SUCCESS", {
        "user": {
            "userId": u.userId,
            "email": u.email,
            "nickname": u.nickname,
            "profileImageUrl": u.profileImageUrl,
        },
        "sessionId": token 
    })


def me(token_user):
    u = token_user
    return ok("AUTH_SUCCESS", {
        "userId": u.userId,
        "email": u.email,
        "nickname": u.nickname,
        "profileImageUrl": u.profileImageUrl,
    })

def email_availability(email: str):
    if not email or not validate_email(email):
        err(400, "INVALID_EMAIL")
    if db.get_user_by_email(email):
        err(409, "EMAIL_ALREADY_EXISTS")
    return ok("EMAIL_AVAILABLE", None)

def nickname_availability(nickname: str):
    if not nickname or not validate_nickname(nickname):
        err(400, "INVALID_NICKNAME")
    if db.get_user_by_nickname(nickname):
        err(409, "NICKNAME_ALREADY_EXISTS")
    return ok("NICKNAME_AVAILABLE", None)

def logout(token: str):
    if not token:
        err(401, "UNAUTHORIZED")
    db.delete_session(token)
    return ok("LOGOUT_SUCCESS", None)
