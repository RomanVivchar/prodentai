"""
Risk assessment router
"""

import json
from typing import Any, Dict, List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import RiskAssessment, User
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class RiskAssessmentRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    questionnaire_data: Dict[str, Any] = Field(..., description="Questionnaire answers")


class RiskAssessmentResponse(BaseModel):
    id: int
    user_id: int
    risk_scores: Dict[str, float]
    recommendations: List[str]
    risk_map: Dict[str, str]  # "green", "yellow", "red"
    created_at: str

    class Config:
        from_attributes = True


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risks(
    request: RiskAssessmentRequest, db: AsyncSession = Depends(get_db)
):
    """Perform risk assessment"""
    # Check if user exists and is active
    from routers.auth_utils import get_user_by_id

    user = await get_user_by_id(request.user_id, db)

    # Используем AI API для оценки рисков
    import logging

    from main import ml_manager

    logger = logging.getLogger(__name__)

    try:
        assessment_result = await ml_manager.assess_risks(request.questionnaire_data)

        # Извлекаем риски и рекомендации из результата ИИ
        risk_scores = {
            "cavity_risk": assessment_result.get("cavity_risk", 0.3),
            "gum_disease_risk": assessment_result.get("gum_disease_risk", 0.2),
            "sensitivity_risk": assessment_result.get("sensitivity_risk", 0.4),
            "enamel_erosion_risk": assessment_result.get("enamel_erosion_risk", 0.1),
        }

        # Используем персональные рекомендации от ИИ, если они есть
        recommendations = assessment_result.get("recommendations", [])

        # Если ИИ не вернул рекомендации, генерируем на основе рисков
        if not recommendations:
            logger.warning(
                "AI did not return recommendations, generating based on risk scores"
            )
            if risk_scores.get("cavity_risk", 0) > 0.5:
                recommendations.append(
                    "Высокий риск кариеса. Используйте зубную пасту с фтором и ограничьте сладости."
                )
            if risk_scores.get("gum_disease_risk", 0) > 0.5:
                recommendations.append(
                    "Риск заболеваний десен. Регулярно используйте зубную нить и посещайте стоматолога."
                )
            if risk_scores.get("sensitivity_risk", 0) > 0.5:
                recommendations.append(
                    "Повышенная чувствительность. Используйте специальную пасту для чувствительных зубов."
                )
            if risk_scores.get("enamel_erosion_risk", 0) > 0.5:
                recommendations.append(
                    "Риск эрозии эмали. Ограничьте потребление кислых напитков и продуктов."
                )

            # Если рекомендаций все еще нет, добавляем общие
            if not recommendations:
                recommendations = [
                    "Продолжайте регулярно чистить зубы",
                    "Посещайте стоматолога каждые 6 месяцев",
                    "Используйте зубную нить ежедневно",
                ]
        else:
            logger.info(
                f"Received {len(recommendations)} personalized recommendations from AI"
            )
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}", exc_info=True)
        # Fallback на mock данные при ошибке
        risk_scores = {
            "cavity_risk": 0.3,
            "gum_disease_risk": 0.2,
            "sensitivity_risk": 0.4,
            "enamel_erosion_risk": 0.1,
        }
        recommendations = [
            "Используйте зубную пасту с фтором",
            "Ограничьте потребление кислых напитков",
            "Регулярно используйте зубную нить",
        ]

    risk_map = {
        "cavity": (
            "green"
            if risk_scores["cavity_risk"] < 0.3
            else "yellow" if risk_scores["cavity_risk"] < 0.6 else "red"
        ),
        "gum_disease": (
            "green"
            if risk_scores["gum_disease_risk"] < 0.3
            else "yellow" if risk_scores["gum_disease_risk"] < 0.6 else "red"
        ),
        "sensitivity": (
            "green"
            if risk_scores["sensitivity_risk"] < 0.3
            else "yellow" if risk_scores["sensitivity_risk"] < 0.6 else "red"
        ),
        "enamel_erosion": (
            "green"
            if risk_scores["enamel_erosion_risk"] < 0.3
            else "yellow" if risk_scores["enamel_erosion_risk"] < 0.6 else "red"
        ),
    }

    # Save assessment to database
    assessment = RiskAssessment(
        user_id=request.user_id,
        assessment_data=request.questionnaire_data,
        risk_scores=risk_scores,
        recommendations=recommendations,
    )

    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    return RiskAssessmentResponse(
        id=assessment.id,
        user_id=assessment.user_id,
        risk_scores=risk_scores,
        recommendations=recommendations,
        risk_map=risk_map,
        created_at=assessment.created_at.isoformat(),
    )


@router.get("/history/{user_id}")
async def get_assessment_history(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's assessment history"""
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.user_id == user_id)
        .order_by(RiskAssessment.created_at.desc())
    )
    assessments = result.scalars().all()

    return [
        {
            "id": assessment.id,
            "risk_scores": assessment.risk_scores,
            "created_at": assessment.created_at.isoformat(),
        }
        for assessment in assessments
    ]


@router.get("/latest/{user_id}")
async def get_latest_assessment(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's latest assessment"""
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.user_id == user_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No assessments found"
        )

    return {
        "id": assessment.id,
        "risk_scores": assessment.risk_scores,
        "recommendations": assessment.recommendations,
        "created_at": assessment.created_at.isoformat(),
    }
