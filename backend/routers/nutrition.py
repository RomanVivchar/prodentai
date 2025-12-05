import json
import os
import tempfile
from typing import Optional

from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from models import NutritionLog, User
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth import get_current_user

router = APIRouter()


class NutritionAnalysisRequest(BaseModel):
    user_id: int
    food_description: str
    weight_grams: Optional[float] = None
    volume_ml: Optional[float] = None
    accompanying_foods: Optional[str] = None
    consumption_duration: Optional[str] = None
    water_after: Optional[bool] = None
    sugar_added: Optional[str] = None
    temperature: Optional[str] = None
    acidity_category: Optional[str] = None
    sensitivity_after: Optional[bool] = None


@router.post("/analyze")
async def analyze_nutrition(
    request: NutritionAnalysisRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze nutrition from text description"""
    try:
        from main import ml_manager

        # Формируем полное описание
        full_description = request.food_description
        if request.accompanying_foods:
            full_description += f". Сопутствующие продукты: {request.accompanying_foods}"

        # Вызываем ML сервис
        analysis_result = await ml_manager.analyze_nutrition(
            food_description=full_description,
            weight_grams=request.weight_grams,
            volume_ml=request.volume_ml,
        )

        # Сохраняем в базу данных
        nutrition_log = NutritionLog(
            user_id=request.user_id,
            food_description=full_description,
            calories=analysis_result.get("calories"),
            sugar_content=analysis_result.get("sugar_content", 0),
            acidity_level=analysis_result.get("acidity_level", 7.0),
            health_score=analysis_result.get("health_score", 5.0),
            recommendations=json.dumps(analysis_result.get("recommendations", [])),
        )
        db.add(nutrition_log)
        await db.commit()

        # Формируем ответ
        return {
            "analysis_result": analysis_result,
            "summary": analysis_result.get("summary", ""),
            "sugar_content": analysis_result.get("sugar_content", 0),
            "acidity_level": analysis_result.get("acidity_level", 7.0),
            "health_score": analysis_result.get("health_score", 5.0),
            "recommendations": analysis_result.get("recommendations", []),
            "weight_grams": request.weight_grams,
            "volume_ml": request.volume_ml,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in nutrition analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-image")
async def analyze_nutrition_image(
    file: UploadFile = File(...),
    user_id: int = Query(...),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze nutrition from uploaded image"""
    try:
        from main import ml_manager

        # Сохраняем файл во временную директорию
        contents = await file.read()
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(contents)
            tmp_path = tmp_file.name

        try:
            # Вызываем ML сервис
            analysis_result = await ml_manager.analyze_nutrition(
                food_description="еда на изображении",
                image_path=tmp_path,
            )

            # Сохраняем в базу данных
            nutrition_log = NutritionLog(
                user_id=user_id,
                food_description="еда на изображении",
                calories=analysis_result.get("calories"),
                sugar_content=analysis_result.get("sugar_content", 0),
                acidity_level=analysis_result.get("acidity_level", 7.0),
                health_score=analysis_result.get("health_score", 5.0),
                recommendations=json.dumps(analysis_result.get("recommendations", [])),
            )
            db.add(nutrition_log)
            await db.commit()

            # Формируем ответ
            return {
                "analysis_result": analysis_result,
                "summary": analysis_result.get("summary", ""),
                "sugar_content": analysis_result.get("sugar_content", 0),
                "acidity_level": analysis_result.get("acidity_level", 7.0),
                "health_score": analysis_result.get("health_score", 5.0),
                "recommendations": analysis_result.get("recommendations", []),
            }
        finally:
            # Удаляем временный файл
            import os as os_module
            try:
                os_module.unlink(tmp_path)
            except:
                pass

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in image nutrition analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
