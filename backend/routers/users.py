"""
Users management router
"""

from typing import List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import NutritionLog, RiskAssessment, User
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class UserProfile(BaseModel):
    id: int
    telegram_id: Optional[int]
    email: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = False  # Отключаем автоматическую сериализацию


class UserStats(BaseModel):
    total_assessments: int
    total_nutrition_logs: int
    last_assessment_date: Optional[str]
    risk_level: Optional[str]


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user profile"""
    from routers.auth_utils import get_user_by_id

    # Для MVP: просто проверяем существование пользователя
    # В будущем можно добавить проверку прав доступа
    user = await get_user_by_id(user_id, db)

    # Преобразуем datetime в строку для Pydantic
    import logging

    logger = logging.getLogger(__name__)

    created_at_str = ""
    if user.created_at:
        try:
            if hasattr(user.created_at, "isoformat"):
                created_at_str = user.created_at.isoformat()
            else:
                created_at_str = str(user.created_at)
        except Exception as e:
            logger.error(f"Error converting created_at to string: {e}")
            created_at_str = ""

    logger.debug(
        f"User created_at type: {type(user.created_at)}, value: {user.created_at}"
    )
    logger.debug(f"Created_at_str: {created_at_str}")

    profile_data = {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "created_at": created_at_str,
    }

    logger.debug(f"Profile data: {profile_data}")

    return UserProfile(**profile_data)


@router.get("/stats/{user_id}", response_model=UserStats)
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user statistics"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get statistics
    total_assessments_result = await db.execute(
        select(func.count(RiskAssessment.id)).where(RiskAssessment.user_id == user_id)
    )
    total_assessments = total_assessments_result.scalar() or 0

    total_nutrition_logs_result = await db.execute(
        select(func.count(NutritionLog.id)).where(NutritionLog.user_id == user_id)
    )
    total_nutrition_logs = total_nutrition_logs_result.scalar() or 0

    last_assessment_result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.user_id == user_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    last_assessment = last_assessment_result.scalar_one_or_none()

    # Вычисляем уровень риска на основе последней оценки
    risk_level = None
    if last_assessment and last_assessment.risk_scores:
        risk_scores = last_assessment.risk_scores
        # Вычисляем средний риск
        avg_risk = (
            risk_scores.get("cavity_risk", 0)
            + risk_scores.get("gum_disease_risk", 0)
            + risk_scores.get("sensitivity_risk", 0)
            + risk_scores.get("enamel_erosion_risk", 0)
        ) / 4

        if avg_risk < 0.3:
            risk_level = "low"
        elif avg_risk < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"

    return UserStats(
        total_assessments=total_assessments,
        total_nutrition_logs=total_nutrition_logs,
        last_assessment_date=(
            last_assessment.created_at.isoformat() if last_assessment else None
        ),
        risk_level=risk_level,  # None если нет оценок
    )


class TelegramLinkRequest(BaseModel):
    telegram_id: int


class TelegramLinkResponse(BaseModel):
    success: bool
    message: str
    telegram_id: Optional[int] = None


@router.post("/link-telegram/{user_id}", response_model=TelegramLinkResponse)
async def link_telegram(
    user_id: int, telegram_data: TelegramLinkRequest, db: AsyncSession = Depends(get_db)
):
    """Link Telegram account to web user account"""
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if telegram_id is already linked to another user
    if telegram_data.telegram_id:
        existing_user_result = await db.execute(
            select(User).where(User.telegram_id == telegram_data.telegram_id)
        )
        existing_user = existing_user_result.scalar_one_or_none()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Telegram account is already linked to another user",
            )

    # Link telegram_id to user
    user.telegram_id = telegram_data.telegram_id
    await db.commit()
    await db.refresh(user)

    return TelegramLinkResponse(
        success=True,
        message="Telegram account linked successfully",
        telegram_id=user.telegram_id,
    )


@router.get("/check-telegram/{user_id}")
async def check_telegram_registration(user_id: int, db: AsyncSession = Depends(get_db)):
    """Check if user is registered in Telegram bot (has telegram_id and has started the bot)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if user has telegram_id
    if not user.telegram_id:
        return {
            "registered": False,
            "has_telegram_id": False,
            "message": "Telegram account not linked",
        }

    # Check if user has started the bot by checking if they have any reminders or other bot activity
    # For now, we'll just check if telegram_id exists (if user started bot, they would have telegram_id)
    # In future, we could add a "bot_started" flag or check for any bot interactions
    return {
        "registered": True,
        "has_telegram_id": True,
        "telegram_id": user.telegram_id,
        "message": "User is registered in Telegram bot",
    }


@router.get("/all-telegram-users")
async def get_all_telegram_users(db: AsyncSession = Depends(get_db)):
    """Get all users with telegram_id (for reminder scheduler)"""
    result = await db.execute(select(User).where(User.telegram_id.isnot(None)))
    users = result.scalars().all()

    return [
        {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "email": user.email,
        }
        for user in users
    ]
