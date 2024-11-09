# auth/utils.py
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from typing import Optional


class TokenService:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        try:
            # Validate environment variables
            if not TokenService.SECRET_KEY:
                raise ValueError("JWT_SECRET_KEY not set in environment variables")

            # Create a copy of the data
            to_encode = data.copy()

            # Set expiration
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES
                )

            # Add expiration to payload
            to_encode.update({"exp": expire})

            # Create JWT token
            encoded_jwt = jwt.encode(
                to_encode, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM
            )

            return encoded_jwt

        except Exception as e:
            print(f"Token creation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not create access token: {str(e)}",
            )

    @staticmethod
    async def verify_token(token: str) -> dict:
        try:
            # Decode and verify the token
            payload = jwt.decode(
                token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM]
            )
            return payload
        except JWTError as e:
            print(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
