from dataclasses import dataclass, field
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

# ---------- Users ----------
@dataclass
class User:
    userId: int
    email: str
    passwordHash: str
    nickname: str
    profileImageUrl: Optional[str]
    createdAt: str
    updatedAt: str

_users: Dict[int, User] = {}
_user_seq = 1
_user_by_email: Dict[str, int] = {}
_user_by_nickname: Dict[str, int] = {}

# ---------- Sessions ----------
_sessions: Dict[str, int] = {}  # sessionId -> userId

# ---------- Posts ----------
@dataclass
class Post:
    postId: int
    title: str
    content: str
    authorUserId: int
    fileUrl: Optional[str]
    hits: int = 0
    likes: Set[int] = field(default_factory=set)
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)

_posts: Dict[int, Post] = {}
_post_seq = 1

# ---------- Comments ----------
@dataclass
class Comment:
    commentId: int
    postId: int
    content: str
    authorUserId: int
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)

_comments: Dict[int, Comment] = {}
_comment_seq = 1

# ---------- User functions ----------
def create_user(email: str, pw_hash: str, nickname: str, profile_url: Optional[str]):
    global _user_seq
    u = User(
        userId=_user_seq,
        email=email,
        passwordHash=pw_hash,
        nickname=nickname,
        profileImageUrl=profile_url,
        createdAt=now_iso(),
        updatedAt=now_iso(),
    )
    _users[_user_seq] = u
    _user_by_email[email] = _user_seq
    _user_by_nickname[nickname] = _user_seq
    _user_seq += 1
    return u

def get_user(user_id: int) -> Optional[User]:
    return _users.get(user_id)

def get_user_by_email(email: str) -> Optional[User]:
    uid = _user_by_email.get(email)
    return _users.get(uid) if uid else None

def get_user_by_nickname(nickname: str) -> Optional[User]:
    uid = _user_by_nickname.get(nickname)
    return _users.get(uid) if uid else None

def delete_user(user_id: int):
    u = _users.pop(user_id, None)
    if not u:
        return
    _user_by_email.pop(u.email, None)
    _user_by_nickname.pop(u.nickname, None)

# ---------- Session functions ----------
def create_session(user_id: int) -> str:
    sid = new_id()
    _sessions[sid] = user_id
    return sid

def delete_session(session_id: str):
    _sessions.pop(session_id, None)

def session_user(session_id: str) -> Optional[User]:
    uid = _sessions.get(session_id)
    return _users.get(uid) if uid else None

# ---------- Post functions ----------
def create_post(title: str, content: str, author_user_id: int, file_url: Optional[str]):
    global _post_seq
    p = Post(
        postId=_post_seq,
        title=title,
        content=content,
        authorUserId=author_user_id,
        fileUrl=file_url,
        createdAt=now_iso(),
        updatedAt=now_iso(),
    )
    _posts[_post_seq] = p
    _post_seq += 1
    return to_post_dict(p)

def update_post(post_id: int, title: str, content: str, file_url: Optional[str]):
    p = _posts.get(post_id)
    if not p:
        return
    p.title = title
    p.content = content
    p.fileUrl = file_url
    p.updatedAt = now_iso()

def delete_post(post_id: int):
    _posts.pop(post_id, None)
    # 연관 댓글 삭제
    for cid in list(_comments.keys()):
        if _comments[cid].postId == post_id:
            _comments.pop(cid, None)

def get_post(post_id: int, increase_hits: bool) -> Optional[dict]:
    p = _posts.get(post_id)
    if not p:
        return None
    if increase_hits:
        p.hits += 1
        p.updatedAt = now_iso()
    return to_post_detail_dict(p)

def list_posts(offset: int, limit: int) -> List[dict]:
    items = list(_posts.values())
    items.sort(key=lambda x: x.postId, reverse=True)
    items = items[offset:] if limit <= 0 else items[offset:offset + limit]

    out = []
    for p in items:
        out.append(to_post_list_dict(p))
    return out

def like_post(post_id: int, user_id: int) -> int:
    p = _posts[post_id]
    p.likes.add(user_id)
    return len(p.likes)

def unlike_post(post_id: int, user_id: int) -> int:
    p = _posts[post_id]
    p.likes.discard(user_id)
    return len(p.likes)

# ---------- Comment functions ----------
def create_comment(post_id: int, content: str, author_user_id: int) -> dict:
    global _comment_seq
    c = Comment(
        commentId=_comment_seq,
        postId=post_id,
        content=content,
        authorUserId=author_user_id,
        createdAt=now_iso(),
        updatedAt=now_iso(),
    )
    _comments[_comment_seq] = c
    _comment_seq += 1
    return to_comment_dict(c)

def get_comment(comment_id: int) -> Optional[dict]:
    c = _comments.get(comment_id)
    return to_comment_dict(c) if c else None

def list_comments(post_id: int) -> List[dict]:
    items = [c for c in _comments.values() if c.postId == post_id]
    items.sort(key=lambda x: x.commentId)
    return [to_comment_dict(c) for c in items]

def update_comment(comment_id: int, content: str):
    c = _comments.get(comment_id)
    if not c:
        return
    c.content = content
    c.updatedAt = now_iso()

def delete_comment(comment_id: int):
    _comments.pop(comment_id, None)

# ---------- serializers ----------
def _comment_count(post_id: int) -> int:
    return sum(1 for c in _comments.values() if c.postId == post_id)

def to_post_list_dict(p: Post) -> dict:
    return {
        "postId": p.postId,
        "title": p.title[:26],
        "authorUserId": p.authorUserId,
        "fileUrl": p.fileUrl,
        "hits": p.hits,
        "likeCount": len(p.likes),
        "commentCount": _comment_count(p.postId),
        "createdAt": p.createdAt,
        "updatedAt": p.updatedAt,
    }

def to_post_dict(p: Post) -> dict:
    return {
        "postId": p.postId,
        "title": p.title,
        "content": p.content,
        "authorUserId": p.authorUserId,
        "fileUrl": p.fileUrl,
        "hits": p.hits,
        "likeCount": len(p.likes),
        "commentCount": _comment_count(p.postId),
        "createdAt": p.createdAt,
        "updatedAt": p.updatedAt,
    }

def to_post_detail_dict(p: Post) -> dict:
    return to_post_dict(p)

def to_comment_dict(c: Comment) -> dict:
    return {
        "commentId": c.commentId,
        "postId": c.postId,
        "content": c.content,
        "authorUserId": c.authorUserId,
        "createdAt": c.createdAt,
        "updatedAt": c.updatedAt,
    }
