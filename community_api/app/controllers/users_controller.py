from fastapi.responses import JSONResponse
from app.storage import memory_store as db
from app.utils.responses import ok, err
from app.utils.security import valid_password, hash_pw

def get_user(user_id: int):
    u = db.get_user(user_id)
    if not u:
        err(404, "NOT_FOUND")
    return ok("USER_RETRIEVED", {
        "userId": u.userId,
        "email": u.email,
        "nickname": u.nickname,
        "profileImageUrl": u.profileImageUrl,
    })

def get_me(u):
    return ok("USER_RETRIEVED", {
        "userId": u.userId,
        "email": u.email,
        "nickname": u.nickname,
        "profileImageUrl": u.profileImageUrl,
    })

def update_me(u, payload: dict):
    nickname = payload.get("nickname")
    if not nickname:
        err(400, "NICKNAME_REQUIRED")
    if len(nickname) > 10:
        err(400, "INVALID_NICKNAME")

    other = db.get_user_by_nickname(nickname)
    if other and other.userId != u.userId:
        err(409, "NICKNAME_ALREADY_EXISTS")

    u.nickname = nickname
    u.updatedAt = db.now_iso()
    return ok("USER_UPDATED", None)

def update_password(u, payload: dict):
    password = payload.get("password")
    password_confirm = payload.get("passwordConfirm")
    if not password:
        err(400, "PASSWORD_REQUIRED")
    if password != password_confirm:
        err(400, "PASSWORD_CONFIRM_MISMATCH")
    if not valid_password(password):
        err(400, "INVALID_PASSWORD")

    u.passwordHash = hash_pw(password)
    u.updatedAt = db.now_iso()
    return ok("PASSWORD_UPDATED", None)

def update_profile_image_url(u, payload: dict):
    url = payload.get("profileImageUrl")
    if not url:
        err(400, "BAD_REQUEST")
    u.profileImageUrl = url
    u.updatedAt = db.now_iso()
    return ok("PROFILE_IMAGE_UPDATED", {"profileImageUrl": url})

def delete_me(u_and_sid):
    u, sid = u_and_sid

    # 유저 삭제(간단 처리)
    db.delete_user(u.userId)
    db.delete_session(sid)

    res = JSONResponse(content=ok("USER_DELETED", None))
    res.delete_cookie("sessionId", path="/")
    return res
