from fastapi import APIRouter, Form, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.controllers import auth_controller as ac
from app.controllers import posts_controller as pc
from app.routers._session import require_user_with_sid, require_user
from app.utils.responses import err

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

COOKIE_KW = dict(
    key="sessionId",
    httponly=True,
    samesite="lax",
    secure=False,
    path="/",
)

@router.post("/signup", status_code=201)
def signup(
    email: str = Form(...),
    password: str = Form(...),
    passwordConfirm: str = Form(...),
    nickname: str = Form(...),
    profile: UploadFile | None = File(None),
):
    if password != passwordConfirm:
        err(400, "PASSWORD_CONFIRM_MISMATCH")

    profile_url = None
    if profile:
        raw = profile.file.read()
        up = pc.save_file(raw, profile.content_type or "application/octet-stream")
        profile_url = up["data"]["fileUrl"]

    return ac.signup(email, password, nickname, profile_url)

@router.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    result = ac.login(email, password)
    session_id = result["data"]["sessionId"]
    user_data = result["data"]["user"]

    res = JSONResponse(content={"code": "LOGIN_SUCCESS", "data": {"user": user_data}})
    res.set_cookie(value=session_id, **COOKIE_KW)
    return res

@router.post("/logout")
def logout(u_and_sid=Depends(require_user_with_sid)):
    _, sid = u_and_sid
    ac.logout(sid)
    res = JSONResponse(content={"code": "LOGOUT_SUCCESS", "data": None})
    res.delete_cookie("sessionId", path="/")
    return res

@router.get("/me")
def me(u=Depends(require_user)):
    return ac.me(u)

@router.get("/emails/availability")
def email_availability(email: str):
    return ac.email_availability(email)

@router.get("/nicknames/availability")
def nickname_availability(nickname: str):
    return ac.nickname_availability(nickname)

