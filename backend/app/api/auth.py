from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.user_service import user_service
from app.utils.security import create_access_token
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(user_in: UserRegister):
    """Register a new user and return JWT access token."""
    try:
        user = await user_service.create_user(user_in)
        access_token = create_access_token(data={"sub": str(user.id)})
        user_resp = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_resp
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user with email and password, returning JWT access token."""
    user = await user_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    user_resp = UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_resp
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get profile information for the authenticated user."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )
