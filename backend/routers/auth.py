from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, get_current_user
from models.schemas import SignUpRequest, LoginRequest, TokenResponse

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user or host",
)
async def signup(body: SignUpRequest):
    db = get_db()

    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user_doc = {
        "name":       body.name,
        "email":      body.email,
        "password":   hash_password(body.password),
        "role":       body.role.value,
        "created_at": datetime.now(timezone.utc),
    }

    result  = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token   = create_access_token({"sub": user_id, "role": body.role.value})

    return TokenResponse(
        access_token=token,
        role=body.role.value,
        name=body.name,
        user_id=user_id,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login for both user and host roles",
)
async def login(body: LoginRequest):
    db   = get_db()
    user = await db.users.find_one({"email": body.email})

    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    user_id = str(user["_id"])
    token   = create_access_token({"sub": user_id, "role": user["role"]})

    return TokenResponse(
        access_token=token,
        role=user["role"],
        name=user["name"],
        user_id=user_id,
    )


@router.get("/me", summary="Get profile of the currently logged-in user/host")
async def me(current_user: dict = Depends(get_current_user)):
    return {
        "id":    str(current_user["_id"]),
        "name":  current_user["name"],
        "email": current_user["email"],
        "role":  current_user["role"],
    }
