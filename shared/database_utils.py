"""
Database utilities for ProDentAI
"""

import asyncio
import logging
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DatabaseUtils:
    """Utility functions for database operations"""

    @staticmethod
    async def get_user_stats(session: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Get total assessments
            result = await session.execute(
                text("SELECT COUNT(*) FROM risk_assessments WHERE user_id = :user_id"),
                {"user_id": user_id},
            )
            total_assessments = result.scalar() or 0

            # Get total nutrition logs
            result = await session.execute(
                text("SELECT COUNT(*) FROM nutrition_logs WHERE user_id = :user_id"),
                {"user_id": user_id},
            )
            total_nutrition_logs = result.scalar() or 0

            # Get last assessment date
            result = await session.execute(
                text(
                    """
                    SELECT created_at FROM risk_assessments 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                ),
                {"user_id": user_id},
            )
            last_assessment = result.scalar()

            return {
                "total_assessments": total_assessments,
                "total_nutrition_logs": total_nutrition_logs,
                "last_assessment_date": (
                    last_assessment.isoformat() if last_assessment else None
                ),
                "risk_level": "medium",  # TODO: Calculate based on latest assessment
            }

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_assessments": 0,
                "total_nutrition_logs": 0,
                "last_assessment_date": None,
                "risk_level": "unknown",
            }

    @staticmethod
    async def get_user_reminders(
        session: AsyncSession, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user reminders"""
        try:
            result = await session.execute(
                text(
                    """
                    SELECT id, reminder_type, time, is_active, message, created_at
                    FROM reminders 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC
                """
                ),
                {"user_id": user_id},
            )

            reminders = []
            for row in result:
                reminders.append(
                    {
                        "id": row.id,
                        "reminder_type": row.reminder_type,
                        "time": row.time,
                        "is_active": row.is_active,
                        "message": row.message,
                        "created_at": row.created_at.isoformat(),
                    }
                )

            return reminders

        except Exception as e:
            logger.error(f"Error getting user reminders: {e}")
            return []

    @staticmethod
    async def get_psychology_history(
        session: AsyncSession, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user psychology session history"""
        try:
            result = await session.execute(
                text(
                    """
                    SELECT id, session_type, user_message, ai_response, sentiment_score, created_at
                    FROM psychology_sessions 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC
                """
                ),
                {"user_id": user_id},
            )

            sessions = []
            for row in result:
                sessions.append(
                    {
                        "id": row.id,
                        "session_type": row.session_type,
                        "user_message": row.user_message,
                        "ai_response": row.ai_response,
                        "sentiment_score": row.sentiment_score,
                        "created_at": row.created_at.isoformat(),
                    }
                )

            return sessions

        except Exception as e:
            logger.error(f"Error getting psychology history: {e}")
            return []

    @staticmethod
    async def get_nutrition_history(
        session: AsyncSession, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user nutrition analysis history"""
        try:
            result = await session.execute(
                text(
                    """
                    SELECT id, food_description, calories, sugar_content, acidity_level, 
                           recommendations, created_at
                    FROM nutrition_logs 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC
                """
                ),
                {"user_id": user_id},
            )

            logs = []
            for row in result:
                logs.append(
                    {
                        "id": row.id,
                        "food_description": row.food_description,
                        "calories": row.calories,
                        "sugar_content": row.sugar_content,
                        "acidity_level": row.acidity_level,
                        "recommendations": row.recommendations,
                        "created_at": row.created_at.isoformat(),
                    }
                )

            return logs

        except Exception as e:
            logger.error(f"Error getting nutrition history: {e}")
            return []

    @staticmethod
    async def get_risk_assessment_history(
        session: AsyncSession, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user risk assessment history"""
        try:
            result = await session.execute(
                text(
                    """
                    SELECT id, risk_scores, recommendations, created_at
                    FROM risk_assessments 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC
                """
                ),
                {"user_id": user_id},
            )

            assessments = []
            for row in result:
                assessments.append(
                    {
                        "id": row.id,
                        "risk_scores": row.risk_scores,
                        "recommendations": row.recommendations,
                        "created_at": row.created_at.isoformat(),
                    }
                )

            return assessments

        except Exception as e:
            logger.error(f"Error getting risk assessment history: {e}")
            return []
