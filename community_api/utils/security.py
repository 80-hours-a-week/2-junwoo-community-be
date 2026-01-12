import re
import hashlib

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PW_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,20}$")  # 8~20, 대/소/숫자/특수 포함

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def validate_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_RE.match(email))

def validate_password_rule(pw: str) -> bool:
    return bool(pw) and bool(PW_RE.match(pw))

def validate_nickname(nickname: str) -> bool:
    return bool(nickname) and (1 <= len(nickname) <= 10)
