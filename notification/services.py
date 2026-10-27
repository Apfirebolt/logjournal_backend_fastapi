from fastapi import HTTPException, status
from typing import List
from . import schema, models
import notification.db as notification_db

async def fetch_notifications(user_id: int) -> List[schema.NotificationResponse]:
    notifications = await notification_db.get_user_notifications(user_id)
    return [schema.NotificationResponse.model_validate(n) for n in notifications]

async def register_notification(user_id: int, request: schema.NotificationCreate) -> schema.NotificationResponse:
    try:
        notification = await notification_db.create_notification(user_id, request)
        return schema.NotificationResponse.model_validate(notification)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

async def set_notification_read(notification_id: int, user_id: int) -> schema.NotificationResponse:
    notification = await notification_db.mark_notification_read(notification_id, user_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return schema.NotificationResponse.model_validate(notification)

async def remove_notification(notification_id: int, user_id: int) -> None:
    success = await notification_db.delete_notification(notification_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return None