from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse
from app.controllers import users_controller as uc
from app.routers._session import require_user

router = APIRouter(prefix="/v1/users", tags=["Users"])

@router.get("/{user_id}")
def get_user(user_id: int):
    return uc.get_user(user_id)

@router.get("/me")
def get_me():
    u, _ = require_user()
    return uc.get_me(u)

@router.patch("/me")
def update_me(nickname: str = Form(...)):
    u, _ = require_user()
    return uc.update_me(u, nickname)

@router.patch("/password")
def update_password(password: str = Form(...), passwordConfirm: str = Form(...)):
    u, _ = require_user()
    return uc.update_password_me(u, password, passwordConfirm)

@router.patch("/me/password")
def update_password_me(password: str = Form(...), passwordConfirm: str = Form(...)):
    u, _ = require_user()
    return uc.update_password_me(u, password, passwordConfirm)

@router.post("/me/profile-image", status_code=201)
def upload_profile_image(profile: UploadFile = File(...)):
    u, _ = require_user()
    return uc.upload_profile_image(u, profile)

@router.delete("/me")
def delete_me():
    u, sid = require_user()
    result = uc.delete_me(u)

    # ✅ 탈퇴 시에도 쿠키 삭제
    res = JSONResponse(content=result)
    res.delete_cookie("sessionId", path="/")
    return res

