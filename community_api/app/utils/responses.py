from fastapi import HTTPException

ERRORS = {
    "EMAIL_REQUIRED": (400, "이메일을 입력해주세요."),
    "PASSWORD_REQUIRED": (400, "비밀번호를 입력해주세요."),
    "PASSWORD_CONFIRM_MISMATCH": (400, "비밀번호 확인이 다릅니다."),
    "INVALID_EMAIL": (400, "올바른 이메일 형식을 입력해주세요."),
    "INVALID_PASSWORD": (400, "비밀번호 형식이 올바르지 않습니다."),
    "NICKNAME_REQUIRED": (400, "닉네임을 입력해주세요."),
    "INVALID_NICKNAME": (400, "닉네임은 1~10자 이내여야 합니다."),
    "EMAIL_ALREADY_EXISTS": (409, "중복된 이메일 입니다."),
    "NICKNAME_ALREADY_EXISTS": (409, "중복된 닉네임 입니다."),
    "UNAUTHORIZED": (401, "아이디 또는 비밀번호를 확인해주세요."),
    "FORBIDDEN": (403, "권한이 없습니다."),
    "NOT_FOUND": (404, "대상을 찾을 수 없습니다."),
    "TITLE_REQUIRED": (400, "제목을 입력해주세요."),
    "TITLE_TOO_LONG": (400, "제목은 최대 26자까지 작성 가능합니다."),
    "CONTENT_REQUIRED": (400, "내용을 입력해주세요."),
    "COMMENT_REQUIRED": (400, "댓글을 입력해주세요."),
}

def ok(code: str, data=None):
    return {"code": code, "data": data}

def err(http_status: int, code: str):
    if code in ERRORS:
        st, msg = ERRORS[code]
        raise HTTPException(status_code=st, detail={"code": code, "message": msg})
    raise HTTPException(status_code=http_status, detail={"code": code, "message": code})
