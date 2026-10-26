from fastapi import HTTPException, status
from typing import List, Optional

from . import schema
from . import models
import auth.db as auth_db


async def new_user_register(request: schema.User) -> models.User:
    try:
        new_user = await auth_db.create_user(request.username, request.email, request.password, role='user')
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while registering the user: {str(e)}"
        )


async def all_users() -> List[models.User]:
    try:
        users = await auth_db.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching all users: {str(e)}"
        )


async def get_user_by_id(user_id: int) -> Optional[models.User]:
    try:
        user_info = await auth_db.get_user_by_id(user_id)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data not found!"
            )

        return user_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the user by ID: {str(e)}"
        )


async def get_profile(current_user: schema.TokenData) -> models.User:
    try:
        user = await auth_db.get_user_by_email(current_user.email)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the user profile: {str(e)}"
        )
