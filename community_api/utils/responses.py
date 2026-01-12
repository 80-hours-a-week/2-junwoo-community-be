from fastapi import HTTPException

def ok(code: str, data=None):
    return {"code": code, "data": data}

def err(status: int, code: str):
    raise HTTPException(status_code=status, detail={"code": code, "data": None})
