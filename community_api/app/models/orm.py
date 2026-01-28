from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import LONGBLOB
from datetime import datetime, timedelta
from app.database import Base

def now_kst():
    return datetime.utcnow() + timedelta(hours=9)

# Many-to-Many relationship for Post Likes
post_likes = Table(
    "post_likes",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class File(Base):
    __tablename__ = "files"
    
    id = Column(String(36), primary_key=True)
    mime_type = Column(String(100), nullable=False)
    # MySQL BLOB (64KB) is too small. Use LONGBLOB (4GB) for images.
    data = Column(LONGBLOB, nullable=False) 
    created_at = Column(DateTime(timezone=True), default=now_kst)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), unique=True, index=True, nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_kst)
    updated_at = Column(DateTime(timezone=True), default=now_kst, onupdate=now_kst)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(36), primary_key=True) # UUID string
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_kst)

    user = relationship("User", back_populates="sessions")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(500), nullable=True)
    hits = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=now_kst)
    updated_at = Column(DateTime(timezone=True), default=now_kst, onupdate=now_kst)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likers = relationship("User", secondary=post_likes, backref="liked_posts")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
