from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Set
import uuid

def now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def new_id() -> str:
    return str(uuid.uuid4())

# ---------- Files ----------
files: Dict[str, bytes] = {}        # file_id -> bytes
file_mimes: Dict[str, str] = {}     # file_id -> mime
file_urls: Dict[str, str] = {}      # file_id -> url (public)

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

_sessions: Dict[str, int] = {}

# ---------- Posts ----------
@dataclass
class Post:
    postId: int
    title: str
    content: str
    authorUserId: int
    fileId: Optional[str]         
    fileUrl: Optional[str]         
    hits: int
    likes: Set[int]                # userId set
    createdAt: str
    updatedAt: str

_posts: Dict[int, Post] = {}
_post_seq = 1

# ---------- Comments ----------
@dataclass
class Comment:
    commentId: int
    postId: int
    content: str
    authorUserId: int
    createdAt: str
    updatedAt: str

_comments: Dict[int, Comment] = {}
_comment_seq = 1

# ---------- helpers ----------
def create_user(email: str, password_hash: str, nickname: str, profile_url: Optional[str]):
    global _user_seq
    uid = _user_seq
    _user_seq += 1
    t = now_iso()
    u = User(uid, email, password_hash, nickname, profile_url, t, t)
    _users[uid] = u
    _user_by_email[email] = uid
    _user_by_nickname[nickname] = uid
    return u

def get_user(user_id: int) -> Optional[User]:
    return _users.get(user_id)

def get_user_by_email(email: str) -> Optional[User]:
    uid = _user_by_email.get(email)
    return _users.get(uid) if uid else None

def get_user_by_nickname(nickname: str) -> Optional[User]:
    uid = _user_by_nickname.get(nickname)
    return _users.get(uid) if uid else None

def create_session(user_id: int) -> str:
    token = new_id()
    _sessions[token] = user_id
    return token

def delete_session(token: str):
    _sessions.pop(token, None)

def session_user(token: str) -> Optional[User]:
    uid = _sessions.get(token)
    return _users.get(uid) if uid else None

def create_post(title: str, content: str, author_user_id: int, file_url: Optional[str]):
    global _post_seq
    pid = _post_seq
    _post_seq += 1
    t = now_iso()
    p = Post(
        postId=pid,
        title=title,
        content=content,
        authorUserId=author_user_id,
        fileId=None,
        fileUrl=file_url,
        hits=0,
        likes=set(),
        createdAt=t,
        updatedAt=t,
    )
    _posts[pid] = p
    return p

def create_comment(post_id: int, content: str, author_user_id: int):
    global _comment_seq
    cid = _comment_seq
    _comment_seq += 1
    t = now_iso()
    c = Comment(cid, post_id, content, author_user_id, t, t)
    _comments[cid] = c
    return c
