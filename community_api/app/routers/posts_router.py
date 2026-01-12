from fastapi import APIRouter, Body, UploadFile, File
from app.controllers import posts_controller as pc
from app.routers._session import require_user

router = APIRouter(prefix="/v1/posts", tags=["Posts"])

@router.get("")
def list_posts(offset: int = 0, limit: int = 0):
    return pc.list_posts(offset, limit)

@router.get("/{post_id}")
def get_post(post_id: int):
    return pc.get_post(post_id)

@router.post("", status_code=201)
def create_post(payload: dict = Body(...)):
    u, _ = require_user()
    return pc.create_post(u, payload.get("title"), payload.get("content"), payload.get("fileUrl"))

@router.patch("/{post_id}")
def update_post(post_id: int, payload: dict = Body(...)):
    u, _ = require_user()
    return pc.update_post(u, post_id, payload.get("title"), payload.get("content"), payload.get("fileUrl"))

@router.delete("/{post_id}")
def delete_post(post_id: int):
    u, _ = require_user()
    return pc.delete_post(u, post_id)

@router.post("/image", status_code=201)
def upload_post_image(postFile: UploadFile = File(...)):
    raw = postFile.file.read()
    return pc.upload_post_image(raw, postFile.content_type or "application/octet-stream")

@router.post("/{post_id}/likes", status_code=201)
def like_post(post_id: int):
    u, _ = require_user()
    return pc.like_post(u, post_id)

@router.delete("/{post_id}/likes")
def unlike_post(post_id: int):
    u, _ = require_user()
    return pc.unlike_post(u, post_id)

@router.get("/{post_id}/comments")
def list_comments(post_id: int):
    return pc.list_comments(post_id)

@router.post("/{post_id}/comments", status_code=201)
def create_comment(post_id: int, payload: dict = Body(...)):
    u, _ = require_user()
    return pc.create_comment(u, post_id, payload.get("content"))

@router.patch("/{post_id}/comments/{comment_id}")
def update_comment(post_id: int, comment_id: int, payload: dict = Body(...)):
    u, _ = require_user()
    return pc.update_comment(u, post_id, comment_id, payload.get("content"))

@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int):
    u, _ = require_user()
    return pc.delete_comment(u, post_id, comment_id)

