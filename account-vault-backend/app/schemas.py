# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime


# ----- User Schemas -----
class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


# ----- Auth Schemas -----
class TokenOut(BaseModel):
    access_token: str
    token_type: str


# ----- Account Schemas -----
class AccountUpsertIn(BaseModel):
    code: str
    image_b64: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    authen: Optional[str] = None
    note: Optional[str] = None


class AccountOut(BaseModel):
    code: str
    image_b64: Optional[str]
    username: Optional[str]
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class SecretOut(BaseModel):
    password: Optional[str]
    authen: Optional[str]


# ----- OTP Schemas -----
class OtpOut(BaseModel):
    otp: Optional[str]
    left: Optional[int]


class OtpBulkIn(BaseModel):
    codes: Optional[list[str]] = []


class OtpBulkOut(BaseModel):
    results: Dict[str, OtpOut]
