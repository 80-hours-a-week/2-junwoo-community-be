from fastapi.responses import JSONResponse
from app.storage import memory_store as db
from app.utils.responses import success_response, success_payload, raise_http_error
from app.utils.security import valid_password, hash_pw


def get_user(user_id: int):
    u = db.get_user(user_id)
    if not u:
        raise_http_error(404, "NOT_FOUND")

    return success_response(
        "USER_RETRIEVED",
        {
            "userId": u["userId"],
            "email": u["email"],
            "nickname": u["nickname"],
            "profileImageUrl": u.get("profileImageUrl"),
        },
    )


def get_me(u):
    return success_response(
        "USER_RETRIEVED",
        {
            "userId": u["userId"],
            "email": u["email"],
            "nickname": u["nickname"],
            "profileImageUrl": u.get("profileImageUrl"),
        },
    )


def update_me(u, payload: dict):
    nickname = payload.get("nickname")
    if not nickname:
        raise_http_error(400, "NICKNAME_REQUIRED")
    if len(nickname) > 10:
        raise_http_error(400, "INVALID_NICKNAME")

    other = db.get_user_by_nickname(nickname)
    if other and other["userId"] != u["userId"]:
        raise_http_error(409, "NICKNAME_ALREADY_EXISTS")

    u["nickname"] = nickname
    u["updatedAt"] = db.now_iso()
    return success_response("USER_UPDATED", None)


def update_password(u, payload: dict):
    password = payload.get("password")
    password_confirm = payload.get("passwordConfirm")
    if not password:
        raise_http_error(400, "PASSWORD_REQUIRED")
    if password != password_confirm:
        raise_http_error(400, "PASSWORD_CONFIRM_MISMATCH")
    if not valid_password(password):
        raise_http_error(400, "INVALID_PASSWORD")

    u["passwordHash"] = hash_pw(password)
    u["updatedAt"] = db.now_iso()
    return success_response("PASSWORD_UPDATED", None)


def update_profile_image_url(u, payload: dict):
    url = payload.get("profileImageUrl")
    if not url:
        raise_http_error(400, "BAD_REQUEST")

    u["profileImageUrl"] = url
    u["updatedAt"] = db.now_iso()

    return success_response("PROFILE_IMAGE_UPDATED", {"profileImageUrl": url})


def delete_me(u_and_sid):
    u, sid = u_and_sid

    db.delete_user(u["userId"])
    db.delete_session(sid)

    res = JSONResponse(content=success_payload("USER_DELETED", None))
    res.delete_cookie("sessionId", path="/")
    return res
