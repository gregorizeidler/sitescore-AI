from typing import Optional
import httpx, time
from jose import jwt
from fastapi import Depends, HTTPException, status, Request
import os

AUTH_JWKS_URL = os.getenv("AUTH_JWKS_URL", "")
AUTH_AUDIENCE = os.getenv("AUTH_AUDIENCE", "")
AUTH_ISSUER = os.getenv("AUTH_ISSUER", "")

class User:
    def __init__(self, sub: str, email: Optional[str] = None):
        self.sub = sub
        self.email = email or sub

_jwks_cache = {"exp": 0, "jwks": None}
async def get_jwks():
    now = int(time.time())
    if _jwks_cache["jwks"] and now < _jwks_cache["exp"]:
        return _jwks_cache["jwks"]
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(AUTH_JWKS_URL)
        r.raise_for_status()
        _jwks_cache["jwks"] = r.json()
        _jwks_cache["exp"] = now + 3600
        return _jwks_cache["jwks"]

async def get_current_user(request: Request) -> User:
    authz = request.headers.get("Authorization", "")
    if not AUTH_JWKS_URL or not authz.startswith("Bearer "):
        ip = request.client.host if request.client else "unknown"
        return User(sub=f"anon:{ip}")
    token = authz.split(" ",1)[1]
    try:
        unverified = jwt.get_unverified_header(token)
        jwks = await get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == unverified["kid"]), None)
        payload = jwt.decode(token, key, algorithms=[key["alg"]], audience=AUTH_AUDIENCE, issuer=AUTH_ISSUER)
        return User(sub=payload.get("sub","unknown"), email=payload.get("email"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
