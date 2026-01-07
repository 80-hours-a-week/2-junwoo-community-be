from fastapi import APIRouter, HTTPException
from app.controllers import community_controller

router = APIRouter()


@router.get("/")
def read_posts():
    return community_controller.get_posts()


@router.post("/")
def create_post(title: str, content: str):
    return community_controller.create_post(title, content)


@router.get("/{post_id}")
def read_post(post_id: int):
    post = community_controller.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글 없음")
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int):
    return community_controller.delete_post(post_id)
