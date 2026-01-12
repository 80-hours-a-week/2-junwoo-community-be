from fastapi import UploadFile
from app.utils.responses import ok, err
from app.utils.security import validate_nickname, validate_password_rule, hash_pw
from app.storage import memory_store as db

def get_user(user_id: int):
    u = db.get_user(user_id)
    if not u:
        err(404, "USER_NOT_FOUND")
    return ok("USER_RETRIEVED", {
        "userId": u.userId,
        "email": u.email,
        "nickname": u.nickname,
        "profileImageUrl": u.profileImageUrl
    })

def get_me(token_user):
    u = token_user
    return ok("USER_RETRIEVED", {
        "userId": u.userId,
        "email": u.email,
        "nickname": u.nickname,
        "profileImageUrl": u.profileImageUrl
    })

def update_me(token_user, nickname: str | None):
    u = token_user

    if nickname is None or nickname == "":
        err(400, "REQUIRED_NICKNAME")
    if not validate_nickname(nickname):
        err(400, "INVALID_NICKNAME")

    other = db.get_user_by_nickname(nickname)
    if other and other.userId != u.userId:
        err(409, "NICKNAME_ALREADY_EXISTS")

    # 인덱스 갱신
    db._user_by_nickname.pop(u.nickname, None)
    u.nickname = nickname
    u.updatedAt = db.now_iso()
    db._user_by_nickname[nickname] = u.userId
    db._users[u.userId] = u

    return ok("USER_UPDATED", None)

def update_password_me(token_user, new_password: str, new_password_confirm: str):
    if not validate_password_rule(new_password):
        err(400, "INVALID_NEW_PASSWORD")
    if new_password != new_password_confirm:
        err(400, "NEW_PASSWORD_CONFIRM_MISMATCH")

    u = token_user
    u.passwordHash = hash_pw(new_password)
    u.updatedAt = db.now_iso()
    db._users[u.userId] = u
    return ok("USER_PASSWORD_UPDATED", None)

def upload_profile_image(token_user, profile: UploadFile):
    raw = profile.file.read()
    if not raw:
        err(400, "INVALID_FILE")

    fid = db.new_id()
    db.files[fid] = raw
    db.file_mimes[fid] = profile.content_type or "application/octet-stream"
    url = f"/public/image/profile/{fid}"
    db.file_urls[fid] = url

    u = token_user
    u.profileImageUrl = url
    u.updatedAt = db.now_iso()
    db._users[u.userId] = u

    return ok("PROFILE_IMAGE_UPLOADED", {"profileImageUrl": url})

def delete_me(token_user):
    u = token_user

    # 1) 작성한 댓글 삭제
    to_del_comments = [cid for cid, c in db._comments.items() if c.authorUserId == u.userId]
    for cid in to_del_comments:
        del db._comments[cid]

    # 2) 작성한 게시글 삭제 (+ 게시글의 댓글도 같이)
    to_del_posts = [pid for pid, p in db._posts.items() if p.authorUserId == u.userId]
    for pid in to_del_posts:
        # 해당 게시글 댓글 삭제
        cids = [cid for cid, c in db._comments.items() if c.postId == pid]
        for cid in cids:
            del db._comments[cid]
        del db._posts[pid]

    # 3) 인덱스/세션 삭제
    db._user_by_email.pop(u.email, None)
    db._user_by_nickname.pop(u.nickname, None)
    db._users.pop(u.userId, None)

    tokens = [t for t, uid in db._sessions.items() if uid == u.userId]
    for t in tokens:
        del db._sessions[t]

    return ok("USER_DELETED", None)
