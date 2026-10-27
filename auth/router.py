from fastapi import APIRouter, status, HTTPException, Depends, File, UploadFile
from typing import List
from . import schema
from . import services
from . import validator
import auth.db as auth_db

from .jwt import create_access_token, get_current_user
from .hashing import verify_password, get_password_hash, is_legacy_bcrypt_hash
from utils.cloudinary_helper import upload_image_to_cloudinary

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
        if not request.email or not request.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")
        
        user = await auth_db.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password")

        # If user had a legacy bcrypt hash, re-hash with Argon2 and update DB
        try:
            if is_legacy_bcrypt_hash(user.password):
                new_hash = get_password_hash(request.password)
                await auth_db.update_user_password(user.id, new_hash)
        except Exception:
            print(f"Warning: failed to rehash password for user {user.email}")

        # Generate a JWT Token including full profile info
        user_data = schema.DisplayAccount(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=getattr(user, 'first_name', None),
            last_name=getattr(user, 'last_name', None),
            profile_image=getattr(user, 'profile_image', None)
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
    return schema.DisplayAccount(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=getattr(user, 'first_name', None),
        last_name=getattr(user, 'last_name', None),
        profile_image=getattr(user, 'profile_image', None)
    )


@router.get('/me', response_model=schema.DisplayAccount)
async def get_current_user_info(current_user: schema.TokenData = Depends(get_current_user)):
    """Get current user information"""
    user = await auth_db.get_user_by_email(current_user.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schema.DisplayAccount(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=getattr(user, 'first_name', None),
        last_name=getattr(user, 'last_name', None),
        profile_image=getattr(user, 'profile_image', None)
    )


@router.put('/profile', response_model=schema.DisplayAccount)
async def update_profile(
    request: schema.UserUpdate,
    current_user: schema.TokenData = Depends(get_current_user)
):
    """Update user username, first name, or last name"""
    updated_user = await services.update_user_profile(current_user.email, request)
    return schema.DisplayAccount(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        first_name=getattr(updated_user, 'first_name', None),
        last_name=getattr(updated_user, 'last_name', None),
        profile_image=getattr(updated_user, 'profile_image', None)
    )


@router.put('/change-password')
async def change_password(
    request: schema.ChangePassword,
    current_user: schema.TokenData = Depends(get_current_user)
):
    """Change logged-in user password"""
    return await services.change_user_password(current_user.email, request)


@router.post('/upload-avatar', response_model=schema.DisplayAccount)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: schema.TokenData = Depends(get_current_user)
):
    """Upload profile image to Cloudinary and attach it to user account"""
    image_url = await upload_image_to_cloudinary(file)
    updated_user = await services.update_profile_image(current_user.email, image_url)
    
    return schema.DisplayAccount(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        first_name=getattr(updated_user, 'first_name', None),
        last_name=getattr(updated_user, 'last_name', None),
        profile_image=getattr(updated_user, 'profile_image', None)
    )