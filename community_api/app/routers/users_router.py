from fastapi import APIRouter, Form, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.controllers import users_controller as uc
from app.controllers import posts_controller as pc
from app.routers._session import require_user, require_user_with_sid

router = APIRouter(prefix="/v1/users", tags=["Users"])

# ✅ 고정 경로 먼저
@router.get("/me")
def get_me(u=Depends(require_user)):
    return uc.get_me(u)

@router.patch("/me")
def update_me(nickname: str = Form(...), u=Depends(require_user)):
    return uc.update_me(u, nickname)

@router.patch("/me/password")
def update_password(password: str = Form(...), passwordConfirm: str = Form(...), u=Depends(require_user)):
    return uc.update_password_me(u, password, passwordConfirm)

@router.post("/me/profile-image", status_code=201)
def upload_profile_image(profile: UploadFile = File(...), u=Depends(require_user)):
    raw = profile.file.read()
    up = pc.save_file(raw, profile.content_type or "application/octet-stream")
    file_url = up["data"]["fileUrl"]
    return uc.upload_profile_image(u, file_url)

@router.delete("/me")
def delete_me(u_and_sid=Depends(require_user_with_sid)):
    u, sid = u_and_sid
    result = uc.delete_me(u)

    res = JSONResponse(content=result)
    res.delete_cookie("sessionId", path="/")
    # 서버 세션도 삭제(선택)
    from app.storage import memory_store as db
    db.delete_session(sid)
    return res

# ✅ 가변 경로는 맨 아래
@router.get("/{user_id:int}")
def get_user(user_id: int):
    return uc.get_user(user_id)

