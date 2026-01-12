from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.storage import memory_store as db

router = APIRouter(prefix="/public/image", tags=["Public"])

@router.get("/profile/{file_id}")
def get_profile_image(file_id: str):
    raw = db.files.get(file_id)
    if raw is None:
        raise HTTPException(status_code=404, detail={"code": "FILE_NOT_FOUND", "data": None})
    mime = db.file_mimes.get(file_id, "application/octet-stream")
    return Response(content=raw, media_type=mime)

@router.get("/post/{file_id}")
def get_post_image(file_id: str):
    raw = db.files.get(file_id)
    if raw is None:
        raise HTTPException(status_code=404, detail={"code": "FILE_NOT_FOUND", "data": None})
    mime = db.file_mimes.get(file_id, "application/octet-stream")
    return Response(content=raw, media_type=mime)
