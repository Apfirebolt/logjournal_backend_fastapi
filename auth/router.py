from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from . import schema
from . import services
from . import validator
import auth.db as auth_db

from . jwt import create_access_token, get_current_user

from . import hashing

router = APIRouter(tags=['Auth'], prefix='/api/auth')


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user_registration(request: schema.User):

    user = await validator.verify_email_exist(request.email)

    if user:
        raise HTTPException(
            status_code=400,
            detail="This user with this email already exists in the system."
        )

    new_user = await services.new_user_register(request)
    return new_user


@router.get('/users', response_model=List[schema.DisplayAccount])
async def get_all_users():
    return await services.all_users()


@router.get('/', response_model=List[schema.DisplayAccount])
async def list_users_root():
    return await services.all_users()


@router.post('/login')
async def login(request: schema.Login):
    try:
        # basic validation for empty fields
        if not request.email or not request.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")
        # fetch user by email from async auth_db
        import auth.db as auth_db
        user = await auth_db.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not hashing.verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password")

        # If user had a legacy bcrypt hash, re-hash with Argon2 and update DB
        try:
            if hashing.is_legacy_bcrypt_hash(user.password):
                new_hash = hashing.get_password_hash(request.password)
                # fire-and-forget update (await to ensure DB consistent)
                await auth_db.update_user_password(user.id, new_hash)
        except Exception:
            # don't fail login if re-hash/update fails; just log
            print(f"Warning: failed to rehash password for user {user.email}")

        # Generate a JWT Token
        user_data = schema.DisplayAccount(
            id=user.id,
            username=user.username,
            email=user.email
        )
        access_token = create_access_token(data={"sub": user_data.email, "id": user_data.id})
        return {"access_token": access_token, "token_type": "bearer", "user": user_data}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.get('/profile', response_model=schema.DisplayAccount)
async def get_profile(current_user: schema.TokenData = Depends(get_current_user)):
    user = await auth_db.get_user_by_email(current_user.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schema.DisplayAccount(id=user.id, username=user.username, email=user.email)


@router.get('/me', response_model=schema.DisplayAccount)
async def get_current_user_info(current_user: schema.TokenData = Depends(get_current_user)):
    """Get current user information"""
    user = await auth_db.get_user_by_email(current_user.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schema.DisplayAccount(id=user.id, username=user.username, email=user.email)










