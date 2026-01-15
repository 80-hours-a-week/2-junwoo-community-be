from datetime import datetime
from typing import Dict, Optional, Set, List
import uuid

def now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def new_id() -> str:
    return str(uuid.uuid4())

# ---------- Files ----------
files: Dict[str, bytes] = {}
file_mimes: Dict[str, str] = {}

# ---------- Users (dict 기반) ----------
_users: Dict[int, dict] = {}
_user_seq = 1
_user_by_email: Dict[str, int] = {}
_user_by_nickname: Dict[str, int] = {}

# ---------- Sessions ----------
_sessions: Dict[str, int] = {}  # sessionId -> userId

# ---------- Posts (dict 기반) ----------
_posts: Dict[int, dict] = {}
_post_seq = 1

# ---------- Comments (dict 기반) ----------
_comments: Dict[int, dict] = {}
_comment_seq = 1


# ---------- User functions ----------
def create_user(email: str, pw_hash: str, nickname: str, profile_url: Optional[str]):
    global _user_seq

    u = {
        "userId": _user_seq,
        "email": email,
        "passwordHash": pw_hash,
        "nickname": nickname,
        "profileImageUrl": profile_url,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    _users[_user_seq] = u
    _user_by_email[email] = _user_seq
    _user_by_nickname[nickname] = _user_seq
    _user_seq += 1
    return u

def get_user(user_id: int) -> Optional[dict]:
    return _users.get(user_id)

def get_user_by_email(email: str) -> Optional[dict]:
    uid = _user_by_email.get(email)
    return _users.get(uid) if uid else None

def get_user_by_nickname(nickname: str) -> Optional[dict]:
    uid = _user_by_nickname.get(nickname)
    return _users.get(uid) if uid else None

def delete_user(user_id: int):
    u = _users.pop(user_id, None)
    if not u:
        return
    _user_by_email.pop(u["email"], None)
    _user_by_nickname.pop(u["nickname"], None)


# ---------- Session functions ----------
def create_session(user_id: int) -> str:
    sid = new_id()
    _sessions[sid] = user_id
    return sid

def delete_session(session_id: str):
    _sessions.pop(session_id, None)

def session_user(session_id: str) -> Optional[dict]:
    uid = _sessions.get(session_id)
    return _users.get(uid) if uid else None


# ---------- Post functions ----------
def create_post(title: str, content: str, author_user_id: int, file_url: Optional[str]):
    global _post_seq
    p = {
        "postId": _post_seq,
        "title": title,
        "content": content,
        "authorUserId": author_user_id,
        "fileUrl": file_url,
        "hits": 0,
        "likes": set(),  # type: Set[int]
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    _posts[_post_seq] = p
    _post_seq += 1
    return to_post_dict(p)

def update_post(post_id: int, title: str, content: str, file_url: Optional[str]):
    p = _posts.get(post_id)
    if not p:
        return
    p["title"] = title
    p["content"] = content
    p["fileUrl"] = file_url
    p["updatedAt"] = now_iso()

def delete_post(post_id: int):
    # delete comments under post too
    for cid in list(_comments.keys()):
        if _comments[cid]["postId"] == post_id:
            _comments.pop(cid, None)
    _posts.pop(post_id, None)

def get_post(post_id: int, increase_hits: bool = True) -> Optional[dict]:
    p = _posts.get(post_id)
    if not p:
        return None
    if increase_hits:
        p["hits"] += 1
    return to_post_dict(p)

def list_posts(offset: int, limit: int) -> List[dict]:
    items = [to_post_dict(_posts[k]) for k in sorted(_posts.keys())]
    if offset < 0:
        offset = 0
    if limit <= 0:
        return items[offset:]
    return items[offset:offset + limit]

def like_post(post_id: int, user_id: int) -> int:
    p = _posts.get(post_id)
    if not p:
        return 0
    p["likes"].add(user_id)
    return len(p["likes"])

def unlike_post(post_id: int, user_id: int) -> int:
    p = _posts.get(post_id)
    if not p:
        return 0
    p["likes"].discard(user_id)
    return len(p["likes"])

def to_post_dict(p: dict) -> dict:
    return {
        "postId": p["postId"],
        "title": p["title"],
        "content": p["content"],
        "authorUserId": p["authorUserId"],
        "fileUrl": p["fileUrl"],
        "hits": p["hits"],
        "likeCount": len(p["likes"]),
        "createdAt": p["createdAt"],
        "updatedAt": p["updatedAt"],
    }


# ---------- Comment functions ----------
def create_comment(post_id: int, content: str, author_user_id: int) -> dict:
    global _comment_seq
    c = {
        "commentId": _comment_seq,
        "postId": post_id,
        "authorUserId": author_user_id,
        "content": content,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    _comments[_comment_seq] = c
    _comment_seq += 1
    return c

def get_comment(comment_id: int) -> Optional[dict]:
    return _comments.get(comment_id)

def update_comment(comment_id: int, content: str):
    c = _comments.get(comment_id)
    if not c:
        return
    c["content"] = content
    c["updatedAt"] = now_iso()

def delete_comment(comment_id: int):
    _comments.pop(comment_id, None)

def list_comments(post_id: int) -> List[dict]:
    items = []
    for cid in sorted(_comments.keys()):
        c = _comments[cid]
        if c["postId"] == post_id:
            items.append(dict(c))
    return items
