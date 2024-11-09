from fastapi import HTTPException, Request, status
from app.services.auth_service import get_current_user
from app.utils.jwt import TokenService
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


from databases import Database

#
# class AuthenticateUserMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, database: Database):
#         super().__init__(app)
#         self.database = database
#
#     async def dispatch(self, request: Request, call_next):
#         try:
#             # Debug print for request path
#             print(f"Processing request path: {request.url.path}")
#
#             # Allow unauthenticated access to login and register endpoints
#             if request.url.path in ["/auth/login", "/auth/register"]:
#                 return await call_next(request)
#
#             # Extract the Authorization header
#             authorization = request.headers.get("Authorization")
#             print(
#                 f"Authorization header: {authorization[:20] if authorization else None}"
#             )
#
#             if not authorization:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Authorization header missing",
#                 )
#
#             # Extract the token
#             try:
#                 scheme, token = authorization.split()
#                 if scheme.lower() != "bearer":
#                     raise HTTPException(
#                         status_code=status.HTTP_401_UNAUTHORIZED,
#                         detail="Invalid authentication scheme",
#                     )
#                 print(f"Extracted token: {token[:10]}...")
#             except ValueError:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Invalid authorization header format",
#                 )
#
#             # Get the current user
#             user = await get_current_user(token, self.database)
#             print(f"Retrieved user: {user['username'] if user else None}")
#
#             if not user:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Invalid authentication credentials",
#                 )
#
#             # Attach the user to the request state
#             request.state.user = user
#             response = await call_next(request)
#             return response
#
#         except HTTPException as e:
#             print(f"HTTP Exception: {e.detail}")
#             return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
#         except Exception as e:
#             print(f"Unexpected error in middleware: {str(e)}")
#             return JSONResponse(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 content={"detail": str(e)},
#             )
#


class AuthenticateUserMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, database: Database):
        super().__init__(app)  # Call the parent class constructor
        self.database = database  # Store the database instance

    async def dispatch(self, request: Request, call_next):
        try:
            if request.url.path in ["/auth/login", "/auth/register"]:
                return await call_next(request)

            authorization = request.headers.get("Authorization")
            if not authorization:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing",
                )

            token = authorization.split(" ")[1]

            # Verify token first
            payload = await TokenService.verify_token(token)

            # Then get user
            user = await get_current_user(payload, self.database)

            request.state.user = user
            return await call_next(request)

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)},
            )
