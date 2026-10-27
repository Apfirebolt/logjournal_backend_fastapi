from fastapi import APIRouter, Depends, status
from typing import List
from . import schema, services
from auth.jwt import get_current_user 

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=List[schema.NotificationResponse])
async def get_notifications(current_user = Depends(get_current_user)):
    user_id = current_user.id
    return await services.fetch_notifications(int(user_id))

@router.patch("/{notification_id}/read", response_model=schema.NotificationResponse)
async def mark_as_read(notification_id: int, current_user = Depends(get_current_user)):
    user_id = current_user.id
    return await services.set_notification_read(notification_id, int(user_id))

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int, current_user = Depends(get_current_user)):
    user_id = current_user.id
    await services.remove_notification(notification_id, int(user_id))
    return {"detail": "Notification deleted successfully"}