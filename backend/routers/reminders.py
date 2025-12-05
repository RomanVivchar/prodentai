"""
Reminders router
"""

from typing import List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Reminder, User
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ReminderCreate(BaseModel):
    user_id: int
    reminder_type: str
    time: str
    date: Optional[str] = None  # Date in YYYY-MM-DD format (for dental_visit)
    message: Optional[str] = None


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    reminder_type: str
    time: str
    date: Optional[str] = None
    is_active: bool
    message: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/create", response_model=ReminderResponse)
async def create_reminder(
    reminder_data: ReminderCreate, db: AsyncSession = Depends(get_db)
):
    """Create new reminder"""
    # Check if user exists
    result = await db.execute(select(User).where(User.id == reminder_data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Set default message if not provided
    if not reminder_data.message:
        if reminder_data.reminder_type == "morning_hygiene":
            reminder_data.message = "Доброе утро! Пора освежить улыбку 😊"
        elif reminder_data.reminder_type == "evening_hygiene":
            reminder_data.message = (
                "Время вечерней гигиены! Не забудьте почистить зубы 🌙"
            )
        elif reminder_data.reminder_type == "dental_visit":
            reminder_data.message = "Напоминание о визите к стоматологу 🦷"

    # Create reminder
    reminder = Reminder(
        user_id=reminder_data.user_id,
        reminder_type=reminder_data.reminder_type,
        time=reminder_data.time,
        date=reminder_data.date,
        message=reminder_data.message,
    )

    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)

    return ReminderResponse(
        id=reminder.id,
        user_id=reminder.user_id,
        reminder_type=reminder.reminder_type,
        time=reminder.time,
        date=reminder.date,
        is_active=reminder.is_active,
        message=reminder.message,
        created_at=reminder.created_at.isoformat(),
    )


@router.get("/user/{user_id}")
async def get_user_reminders(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's reminders"""
    result = await db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .order_by(Reminder.created_at.desc())
    )
    reminders = result.scalars().all()

    return [
        {
            "id": reminder.id,
            "reminder_type": reminder.reminder_type,
            "time": reminder.time,
            "date": reminder.date,
            "is_active": reminder.is_active,
            "message": reminder.message,
            "created_at": reminder.created_at.isoformat(),
        }
        for reminder in reminders
    ]


class ToggleRequest(BaseModel):
    is_active: Optional[bool] = None


@router.put("/toggle/{reminder_id}")
async def toggle_reminder(
    reminder_id: int, 
    request: ToggleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Toggle reminder active status"""
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found"
        )

    # If is_active is provided in request, use it, otherwise toggle
    if request.is_active is not None:
        reminder.is_active = request.is_active
    else:
        reminder.is_active = not reminder.is_active
    
    await db.commit()

    return {
        "id": reminder.id,
        "is_active": reminder.is_active,
        "message": "Reminder status updated",
    }


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, db: AsyncSession = Depends(get_db)):
    """Delete reminder"""
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found"
        )

    await db.execute(delete(Reminder).where(Reminder.id == reminder_id))
    await db.commit()

    return {"message": "Reminder deleted successfully"}


@router.get("/types")
async def get_reminder_types():
    """Get available reminder types"""
    types = [
        {
            "type": "morning_hygiene",
            "name": "Утренняя гигиена",
            "description": "Напоминание о чистке зубов утром",
            "default_time": "08:00",
        },
        {
            "type": "evening_hygiene",
            "name": "Вечерняя гигиена",
            "description": "Напоминание о чистке зубов вечером",
            "default_time": "22:00",
        },
        {
            "type": "dental_visit",
            "name": "Визит к стоматологу",
            "description": "Напоминание о запланированном визите",
            "default_time": "10:00",
        },
        {
            "type": "floss",
            "name": "Использование зубной нити",
            "description": "Напоминание о чистке межзубных промежутков",
            "default_time": "21:00",
        },
    ]

    return {"types": types}
