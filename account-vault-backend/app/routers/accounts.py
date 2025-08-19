# app/routers/accounts.py
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account
from ..schemas import (
    AccountUpsertIn,
    AccountOut,
    SecretOut,
    OtpOut,
    OtpBulkIn,
    OtpBulkOut,
)
from ..security import encrypt_maybe, decrypt_maybe, totp6, totp_left
from .auth import get_current_user, User  # current user dependency

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=List[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = db.query(Account).order_by(Account.updated_at.desc().nullslast()).all()
    return [
        AccountOut(
            code=r.code,
            image_b64=r.image_b64,
            username=r.username,
            note=r.note,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.post("", response_model=AccountOut)
def upsert_account(
    payload: AccountUpsertIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = db.query(Account).filter(Account.code == payload.code).first()
    if not r:
        r = Account(code=payload.code)
        db.add(r)

    # set/overwrite các field không nhạy cảm
    if payload.image_b64 is not None:
        r.image_b64 = payload.image_b64
    if payload.username is not None:
        r.username = payload.username
    if payload.note is not None:
        r.note = payload.note

    # Chỉ cập nhật secrets nếu client gửi field (None = không đụng tới)
    if payload.password is not None:
        r.password_enc = encrypt_maybe(payload.password) if payload.password != "" else None
    if payload.authen is not None:
        r.authen_enc = encrypt_maybe(payload.authen) if payload.authen != "" else None

    db.commit()
    db.refresh(r)
    return AccountOut(
        code=r.code,
        image_b64=r.image_b64,
        username=r.username,
        note=r.note,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.delete("/{code}")
def delete_account(
    code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = db.query(Account).filter(Account.code == code).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"ok": True}


@router.get("/{code}/secrets", response_model=SecretOut)
def get_secrets(
    code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = db.query(Account).filter(Account.code == code).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return SecretOut(
        password=decrypt_maybe(r.password_enc),
        authen=decrypt_maybe(r.authen_enc),
    )


@router.get("/{code}/otp", response_model=OtpOut)
def get_otp_single(
    code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = db.query(Account).filter(Account.code == code).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    secret = decrypt_maybe(r.authen_enc)
    if not secret:
        return OtpOut(otp=None, left=None)
    return OtpOut(otp=totp6(secret), left=totp_left())


@router.post("/otp/bulk", response_model=OtpBulkOut)
def get_otp_bulk(
    payload: OtpBulkIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    codes = payload.codes or []
    rows = db.query(Account).filter(Account.code.in_(codes)).all() if codes else []
    map_rows: Dict[str, Account] = {r.code: r for r in rows}

    out: Dict[str, OtpOut] = {}
    for code in codes:
        r = map_rows.get(code)
        if not r:
            out[code] = OtpOut(otp=None, left=None)
            continue
        secret = decrypt_maybe(r.authen_enc)
        out[code] = OtpOut(
            otp=totp6(secret) if secret else None,
            left=totp_left() if secret else None,
        )
    return OtpBulkOut(results=out)
