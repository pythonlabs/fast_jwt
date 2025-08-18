# src/fast_jwt/__init__.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class FastJWT:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, user_id: str | int, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token d'accès."""
        to_encode = {"sub": str(user_id)}

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Par défaut, le token expire dans 15 minutes
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "jwt_type": "access_token"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, user_id: int | str, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token d'accès."""
        to_encode = {"sub": str(user_id)}
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Par défaut, le token expire dans 3 jours
            expire = datetime.now(timezone.utc) + timedelta(days=3)

        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "jwt_type": "refresh_token"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def refresh_token(self, token: str = Depends(oauth2_scheme)):
        """Rafraîchit un token d'accès."""
        payload = self._decode_token(token)
        if payload.get("jwt_type") != "refresh_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        access_token = self.create_access_token(user_id)
        refresh_token = self.create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def _decode_token(self, token: str) -> Dict[str, Any]:
        """Décode et valide un token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def auth_required(self, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
        """
        Dépendance FastAPI pour protéger une route.
        Utilisation : app.get("/protected", dependencies=[Depends(jwt_auth.auth_required)])
        """
        payload = self._decode_token(token)
        if payload.get("jwt_type") != "access_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> str:
        """
        Dépendance FastAPI qui retourne le payload du token (les données de l'utilisateur).
        Utilisation : def get_user_data(user_id: = Depends(jwt_auth.get_current_user)): ...
        """
        payload = self._decode_token(token)
        if payload.get("jwt_type") != "access_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload.get("sub")