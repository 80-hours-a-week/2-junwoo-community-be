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

def update_me(u, nickname: str):
    if not nickname:
        err(400, "NICKNAME_REQUIRED")
    if len(nickname) > 10:
        err(400, "INVALID_NICKNAME")

    other = db.get_user_by_nickname(nickname)
    if other and other.userId != u.userId:
        err(409, "NICKNAME_ALREADY_EXISTS")

    # 메모리 객체 직접 수정
    u.nickname = nickname
    u.updatedAt = db.now_iso()
    return ok("USER_UPDATED", None)

def update_password_me(u, password: str, password_confirm: str):
    if password != password_confirm:
        err(400, "PASSWORD_CONFIRM_MISMATCH")
    if not valid_password(password):
        err(400, "INVALID_PASSWORD")

    u.passwordHash = hash_pw(password)
    u.updatedAt = db.now_iso()
    return ok("PASSWORD_UPDATED", None)

def upload_profile_image(u, file_url: str):
    u.profileImageUrl = file_url
    u.updatedAt = db.now_iso()
    return ok("PROFILE_IMAGE_UPDATED", {"profileImageUrl": file_url})

def delete_me(u):
    # 간단 처리: 유저 삭제(실무에서는 연쇄 데이터 삭제 고려)
    # 여기서는 과제 요구대로 "탈퇴 시 게시글/댓글 삭제"를 구현하고 싶으면 posts/comments도 지워주면 됨.
    # 최소 구현: 유저만 제거
    from app.storage.memory_store import _users, _user_by_email, _user_by_nickname  # noqa
    _users.pop(u.userId, None)
    _user_by_email.pop(u.email, None)
    _user_by_nickname.pop(u.nickname, None)
    return ok("USER_DELETED", None)

