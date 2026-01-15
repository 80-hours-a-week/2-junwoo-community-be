from fastapi import APIRouter
from fastapi.responses import Response
from app.storage import memory_store as db
from app.utils.responses import raise_http_error

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/files/{file_id}")
def get_file(file_id: str):
    raw = db.files.get(file_id)
    if raw is None:
        raise_http_error(404, "NOT_FOUND")
    mime = db.file_mimes.get(file_id, "application/octet-stream")
    return Response(content=raw, media_type=mime)
