# app/security.py
import base64, hashlib, hmac, time
from typing import Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from .config import JWT_SECRET, JWT_ALG, JWT_EXPIRE, APP_SECRET

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Derive a stable Fernet key from APP_SECRET
FERNET_KEY = base64.urlsafe_b64encode(hashlib.sha256(APP_SECRET.encode()).digest())
fer = Fernet(FERNET_KEY)

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hp: str) -> bool:
    return pwd_context.verify(p, hp)

def create_access_token(sub: str) -> str:
    now = datetime.now(tz=timezone.utc)
    exp = now + JWT_EXPIRE
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decrypt_maybe(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    try:
        v = fer.decrypt(token.encode(), ttl=None)
        return v.decode()
    except Exception:
        return None

def encrypt_maybe(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return fer.encrypt(value.encode()).decode()

# TOTP 6 digits, period=180, SHA1 (Garena)
_DEF_PERIOD = 180

def _int_to_bytes(i: int) -> bytes:
    return i.to_bytes(8, "big")

def totp6(base32_secret: str, period: int = _DEF_PERIOD, for_time: Optional[int] = None) -> Optional[str]:
    if not base32_secret:
        return None
    try:
        s = base64.b32decode(base32_secret.upper().encode(), casefold=True)
    except Exception:
        return None
    ts = int(for_time or time.time())
    counter = ts // period
    msg = _int_to_bytes(counter)
    digest = hmac.new(s, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = ((digest[offset] & 0x7F) << 24) | (digest[offset + 1] << 16) | (digest[offset + 2] << 8) | (digest[offset + 3])
    otp = code % 1_000_000
    return f"{otp:06d}"

def totp_left(period: int = _DEF_PERIOD, for_time: Optional[int] = None) -> int:
    ts = int(for_time or time.time())
    return period - (ts % period)
