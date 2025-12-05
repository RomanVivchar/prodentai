"""
ML Services for ProDentAI
Использует OpenAI API вместо локальных моделей
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class MLServiceManager:
    """Manager for all ML services using API"""

    def __init__(self):
        # Настройка OpenAI API клиента
        # В Docker переменные окружения уже загружены через env_file
        # Но на всякий случай попробуем загрузить .env если он есть
        from dotenv import load_dotenv

        load_dotenv()

        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("AI_MODEL", "gpt-3.5-turbo")

        # Инициализация OpenAI клиента
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(
                f"Initialized ML Service with OpenAI API (model: {self.model_name})"
            )
        else:
            self.client = None
            logger.warning(
                "OPENAI_API_KEY not set, AI features will use fallback responses"
            )

    async def initialize_models(self):
        """Initialize API connection"""
        try:
            if not self.api_key:
                logger.warning("AI API key not set. Using mock responses.")
            else:
                logger.info(f"OpenAI API initialized (model: {self.model_name})")
        except Exception as e:
            logger.error(f"Error initializing AI API: {e}")

    async def _call_ai_api(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> str:
        """Вызов OpenAI API"""
        if not self.client:
            logger.warning("AI API not configured, returning empty response")
            return ""

        if not self.api_key:
            logger.warning("AI API key not set, returning empty response")
            return ""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Используем переопределенную модель, если указана, иначе базовую
            model_to_use = model_override or self.model_name
            logger.debug(f"Calling OpenAI API with model {model_to_use}")

            # Некоторые модели (например, gpt-5-nano) имеют особые требования к параметрам
            create_params = {
                "model": model_to_use,
                "messages": messages,
            }

            # Проверяем, какая модель используется
            is_new_model = (
                "gpt-5" in model_to_use.lower() or "o1" in model_to_use.lower()
            )

            if is_new_model:
                # Новые модели используют max_completion_tokens и не поддерживают temperature
                # Увеличиваем лимит для моделей gpt-5/o1, так как они могут требовать больше токенов
                # Для моделей с reasoning (o1) нужно больше токенов, так как reasoning tokens не считаются в completion
                create_params["max_completion_tokens"] = (
                    4000  # Увеличено с 2000 до 4000
                )
                # temperature не передаем - используется значение по умолчанию (1)
            else:
                # Старые модели используют max_tokens и temperature
                create_params["max_tokens"] = 1000
                create_params["temperature"] = 0.7

            response = await self.client.chat.completions.create(**create_params)

            # Детальное логирование для отладки
            logger.info(
                f"  Response received: {len(response.choices) if response.choices else 0} choices"
            )

            if response and response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                content = choice.message.content

                # Логируем детали для диагностики
                logger.info(f"  ✓ Response details:")
                logger.info(f"    - Finish reason: {choice.finish_reason}")
                logger.info(
                    f"    - Content length: {len(content) if content else 0} chars"
                )
                logger.info(
                    f"    - Usage: {response.usage.model_dump() if hasattr(response, 'usage') and response.usage else 'N/A'}"
                )

                if content and content.strip():
                    logger.info(f"  ✓ Response content preview: {content[:200]}...")
                    logger.debug(f"  Full response: {content}")
                    logger.info("=" * 60)
                    return content.strip()
                else:
                    logger.warning(f"  ✗ Empty content returned")
                    logger.warning(f"    Finish reason: {choice.finish_reason}")

                    # Если finish_reason не 'stop', это может быть проблема
                    if choice.finish_reason == "length":
                        logger.warning(
                            "    ⚠ Response was truncated due to token limit"
                        )
                        logger.warning(
                            f"    Current limit: {create_params.get('max_completion_tokens', create_params.get('max_tokens', 'N/A'))}"
                        )
                        logger.warning(
                            "    Consider increasing token limit or reducing prompt size"
                        )
                    elif choice.finish_reason == "content_filter":
                        logger.warning("    ⚠ Response was filtered by content filter")
                    elif choice.finish_reason:
                        logger.warning(
                            f"    ⚠ Unexpected finish_reason: {choice.finish_reason}"
                        )

                    # Логируем полный объект choice для отладки
                    logger.debug(f"    Full choice: {choice}")
                    logger.debug(f"    Choice message: {choice.message}")
                    logger.info("=" * 60)
                    return ""
            else:
                logger.warning(f"  ✗ No choices in response")
                logger.warning(f"    Response object: {response}")
                logger.info("=" * 60)
                return ""

        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"✗ Error calling AI API: {type(e).__name__}")
            logger.error(f"  Error message: {str(e)}")
            logger.error(f"  Model: {self.model_name}")
            logger.error(f"  System prompt length: {len(system_prompt)}")
            logger.error(f"  User prompt length: {len(user_prompt)}")
            logger.error("  Full traceback:", exc_info=True)
            logger.error("=" * 60)
            # Не пробрасываем ошибку, возвращаем пустую строку для fallback
            return ""

    async def assess_risks(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess dental risks based on questionnaire using AI and generate personalized recommendations"""
        try:
            # Используем модель без reasoning для структурированного анализа
            risk_model = (
                "gpt-4o"
                if "gpt-5" in self.model_name.lower() or "o1" in self.model_name.lower()
                else self.model_name
            )
            logger.info(
                f"Using model for risk assessment: {risk_model} (base model: {self.model_name})"
            )

            # Формируем промпт для оценки рисков с персональными рекомендациями
            system_prompt = """Ты - эксперт-стоматолог, который анализирует анкеты пациентов и оценивает риски стоматологических заболеваний.

Твоя задача - проанализировать ответы пациента и вернуть ТОЛЬКО валидный JSON в формате:
{
    "cavity_risk": число от 0.0 до 1.0 (риск кариеса),
    "gum_disease_risk": число от 0.0 до 1.0 (риск заболеваний десен),
    "sensitivity_risk": число от 0.0 до 1.0 (риск чувствительности зубов),
    "enamel_erosion_risk": число от 0.0 до 1.0 (риск эрозии эмали),
    "recommendations": ["персональная рекомендация 1", "персональная рекомендация 2", "персональная рекомендация 3", ...]
}

КРИТИЧЕСКИ ВАЖНО для рекомендаций:
- Рекомендации должны быть ПЕРСОНАЛИЗИРОВАННЫМИ на основе конкретных ответов пациента
- Учитывай все факторы: наследственность, питание, гигиену, привычки, состояние здоровья
- Рекомендации должны быть конкретными и практичными (3-7 рекомендаций)
- Используй информацию из ответов для создания индивидуальных советов
- Примеры хороших рекомендаций:
  * "Учитывая частые перекусы и употребление сладких напитков, рекомендую ограничить их до 1-2 раз в неделю и полоскать рот водой после каждого приема пищи"
  * "Так как у вас есть наследственная предрасположенность к проблемам с деснами, важно использовать зубную нить ежедневно и посещать стоматолога каждые 3-4 месяца"
  * "При наличии бруксизма и скрежета зубов рекомендую использовать капу на ночь и обратиться к стоматологу для изготовления индивидуальной защиты"

Оценка рисков:
- 0.0-0.3: низкий риск (зеленый)
- 0.3-0.6: средний риск (желтый)
- 0.6-1.0: высокий риск (красный)

Учитывай при оценке:
- Наследственность: если есть семейная история проблем - повышай соответствующие риски
- Питание: частое употребление сладкого/кислого повышает риски кариеса и эрозии
- Гигиена: плохая гигиена повышает все риски
- Привычки: бруксизм, дыхание ртом, жевание твердых предметов повышают соответствующие риски
- Состояние: кровоточивость десен, чувствительность, сухость во рту - важные индикаторы"""

            user_prompt = f"""Проанализируй следующие ответы пациента из анкеты:
{json.dumps(questionnaire_data, ensure_ascii=False, indent=2)}

Оцени риски для каждого типа заболевания и создай персональные рекомендации на основе конкретных ответов пациента.
Верни ТОЛЬКО валидный JSON с оценками рисков и рекомендациями."""

            if self.client:
                response = await self._call_ai_api(
                    system_prompt, user_prompt, model_override=risk_model
                )
                if response:
                    try:
                        # Пытаемся извлечь JSON из ответа
                        json_start = response.find("{")
                        json_end = response.rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            result = json.loads(response[json_start:json_end])
                            logger.info(
                                f"Risk assessment completed: {len(result.get('recommendations', []))} recommendations"
                            )
                            return result
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse AI response as JSON: {e}")
                        logger.debug(f"Response was: {response[:500]}")

            # Fallback на mock данные
            logger.warning("Using fallback risk assessment")
            default_risks = self._get_default_risks()
            return {
                **default_risks,
                "recommendations": [
                    "Используйте зубную пасту с фтором",
                    "Ограничьте потребление кислых напитков",
                    "Регулярно используйте зубную нить",
                ],
            }

        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return self._get_default_risks()

    async def analyze_nutrition(
        self,
        food_description: str,
        image_path: Optional[str] = None,
        weight_grams: Optional[float] = None,
        volume_ml: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Analyze nutrition from text or image using AI"""
        try:
            if not self.client:
                logger.warning("AI client not initialized, using fallback")
                return await self._analyze_food_text(food_description)

            # Используем базовую модель для nutrition analysis
            nutrition_model = self.model_name
            logger.info(f"Using model for nutrition analysis: {nutrition_model}")

            system_prompt = """Ты - эксперт-диетолог и стоматолог, который анализирует еду и оценивает её влияние на здоровье зубов.

Твоя задача - провести детальный анализ еды и вернуть ТОЛЬКО валидный JSON в формате:
{
    "food_items": ["список", "продуктов", "в", "именительном", "падеже"],
    "summary": "ОБЯЗАТЕЛЬНО: краткое описание блюда (2-3 предложения) с учетом всех указанных продуктов и сопутствующих блюд. Это поле ОБЯЗАТЕЛЬНО должно быть заполнено!",
    "sugar_content": число (граммы сахара с учетом указанного веса/объема),
    "acidity_level": число (pH от 0 до 14, где 7 - нейтральный, очень точно определи pH),
    "acidity_category": строка ("кислое" если pH < 5.5, "сладкое" если много сахара, "нейтральное" если pH 6.5-7.5),
    "health_score": число (от 0 до 10, где 10 - очень полезно для зубов),
    "recommendations": ["рекомендация 1", "рекомендация 2"]
}

КРИТИЧЕСКИ ВАЖНО для summary:
- Поле summary ОБЯЗАТЕЛЬНО должно быть заполнено в каждом ответе!
- Напиши 2-3 предложения о блюде
- Упомяни все основные продукты
- Если указаны сопутствующие продукты, обязательно включи их в описание
- Опиши состав и особенности блюда с точки зрения стоматологии
- Примеры:
  * "Макароны с мясом представляют собой углеводно-белковое блюдо. Макароны содержат крахмал, который может способствовать образованию налета, а мясо является источником белка. В целом блюдо имеет нейтральную кислотность."
  * "Чай с сахаром - это горячий напиток, содержащий кофеин и добавленный сахар. Сахар способствует развитию кариеса, а высокая температура может вызывать чувствительность зубов."

КРИТИЧЕСКИ ВАЖНО для food_items:
1. Убери ВСЕ предлоги (с, в, на, для, и, из, от, к, по, под, над, при, про, без, через) из списка продуктов
2. Приведи ВСЕ продукты к именительному падежу (единственное число)
3. Разделяй только на отдельные продукты, не на слова
4. НЕ включай категории типа "сопутствующие", "основные", "продукты" - только названия продуктов
5. НЕ включай знаки препинания в конце слов
6. Примеры:
   - "Макароны с мясом" → ["макароны", "мясо"] (НЕ ["макароны", "с", "мясом", "мясом."])
   - "Салат из помидоров и огурцов" → ["салат", "помидор", "огурец"] (НЕ ["салат", "из", "помидоров", "и", "огурцов"])
   - "Кофе с молоком и сахаром" → ["кофе", "молоко", "сахар"] (НЕ ["кофе", "с", "молоком", "и", "сахаром"])
   - "Пицца с сыром" → ["пицца", "сыр"] (НЕ ["пицца", "с", "сыром"])
   - "Макароны с мясом. Сопутствующие продукты: чай" → ["макароны", "мясо", "чай"] (НЕ ["макароны", "с", "мясом", "Сопутствующие", "продукты", "чай"])

ВАЖНО для acidity_level:
- Определяй pH очень точно на основе реальных значений продуктов
- Цитрусы (лимон, апельсин): pH 2.0-3.0
- Газированные напитки: pH 2.5-3.5
- Вино: pH 3.0-3.5
- Яблоки: pH 3.3-4.0
- Помидоры: pH 4.0-4.5
- Молоко: pH 6.5-6.7
- Вода: pH 7.0
- Сыр: pH 5.0-6.0
- Хлеб: pH 5.0-6.0

ВАЖНО: Если указан вес (граммы) или объем (мл), учитывай это при расчете сахара.
Например, если указано "яблоко, 200г", то сахар должен быть для 200г яблока, а не для стандартной порции.

Примеры:
- Сладкие продукты (конфеты, газировка): высокий sugar_content, низкий health_score, acidity_category="сладкое"
- Кислые продукты (цитрусы, уксус): низкий acidity_level (< 5.5), acidity_category="кислое", рекомендация подождать перед чисткой
- Полезные продукты (сыр, овощи): высокий health_score, низкий sugar_content, acidity_category="нейтральное" или "кислое" (для овощей)"""

            # Формируем промпт с учетом веса и объема
            user_context = ""
            if weight_grams:
                user_context += f"\nВАЖНО: Указан вес: {weight_grams} грамм. Рассчитай калории и сахар именно для этого веса."
            if volume_ml:
                user_context += f"\nВАЖНО: Указан объем: {volume_ml} мл. Рассчитай калории и сахар именно для этого объема."

            if image_path:
                # Анализ изображения через Vision API
                return await self._analyze_nutrition_image(
                    image_path,
                    food_description,
                    system_prompt,
                    weight_grams,
                    volume_ml,
                    nutrition_model,
                )
            else:
                # Анализ текста
                user_prompt = f"""Проанализируй следующее описание еды: "{food_description}"{user_context}

КРИТИЧЕСКИ ВАЖНО: 
1. Поле summary ОБЯЗАТЕЛЬНО должно быть заполнено в JSON ответе! 
2. Напиши 2-3 предложения о блюде в поле summary.
3. В summary включи описание ВСЕХ продуктов из основного блюда и сопутствующих продуктов (если они указаны в описании).
4. Опиши состав и особенности блюда с точки зрения стоматологии.

Верни детальный анализ в формате JSON с указанными полями. НЕ ЗАБУДЬ включить поле summary!"""

                logger.info(
                    f"Calling AI API for nutrition analysis: {food_description[:50]}..."
                )
                logger.debug(
                    f"User context: {user_context[:200] if user_context else 'None'}..."
                )
                # Используем специальную модель для nutrition analysis
                response = await self._call_ai_api(
                    system_prompt, user_prompt, model_override=nutrition_model
                )

                if response:
                    logger.debug(f"AI Response (first 500 chars): {response[:500]}...")
                    try:
                        # Извлекаем JSON из ответа
                        json_start = response.find("{")
                        json_end = response.rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            analysis = json.loads(response[json_start:json_end])
                            logger.info(
                                f"Nutrition analysis completed: {len(analysis.get('food_items', []))} items found"
                            )
                            # Проверяем наличие summary
                            if "summary" in analysis and analysis["summary"]:
                                logger.info(
                                    f"✓ Summary found in AI response: {analysis['summary'][:100]}..."
                                )
                            else:
                                logger.warning(f"✗ Summary NOT found in AI response!")
                                logger.warning(
                                    f"  Response keys: {list(analysis.keys())}"
                                )
                                logger.warning(
                                    f"  Full response (first 1000 chars): {response[:1000]}"
                                )
                                # Добавляем fallback summary
                                food_items_str = ", ".join(
                                    analysis.get("food_items", ["продукты"])[:3]
                                )
                                analysis["summary"] = (
                                    f"Блюдо содержит {food_items_str}. Не удалось провести детальный анализ. Попробуйте описать еду более подробно."
                                )
                            return analysis
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse AI response as JSON: {e}")
                        logger.debug(f"Response was: {response[:200]}")

            # Fallback на mock данные
            logger.warning("Using fallback nutrition analysis")
            return await self._analyze_food_text(food_description)

        except Exception as e:
            logger.error(f"Error in nutrition analysis: {e}", exc_info=True)
            return self._get_default_nutrition()

    async def _analyze_nutrition_image(
        self,
        image_path: str,
        food_description: Optional[str],
        system_prompt: str,
        weight_grams: Optional[float] = None,
        volume_ml: Optional[float] = None,
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze nutrition from image using OpenAI Vision API"""
        try:
            import base64

            # Читаем изображение и кодируем в base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")

            # Определяем MIME тип
            if image_path.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_path.lower().endswith(".webp"):
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"

            user_context = ""
            if weight_grams:
                user_context += f"\nВАЖНО: Указан вес: {weight_grams} грамм. Рассчитай калории и сахар именно для этого веса."
            if volume_ml:
                user_context += f"\nВАЖНО: Указан объем: {volume_ml} мл. Рассчитай калории и сахар именно для этого объема."

            user_prompt = f"""Проанализируй изображение и определи, какие продукты питания на нем представлены. Это медицинское приложение для анализа питания в контексте стоматологического здоровья.

Задача: определить состав блюда для оценки влияния на здоровье зубов.

{f'Если изображение нечеткое, используй описание: "{food_description}"' if food_description else ''}{user_context}

Верни результат в формате JSON:
{{
  "food_items": ["список", "продуктов"],
  "sugar_content": число,
  "acidity_level": число,
  "health_score": число,
  "summary": "краткое описание блюда 2-3 предложения",
  "recommendations": ["рекомендация 1", "рекомендация 2"]
}}

Пример:
{{
  "food_items": ["яйцо", "бекон"],
  "sugar_content": 0.5,
  "acidity_level": 6.5,
  "health_score": 7.0,
  "summary": "На изображении яичница с беконом. Яйца - источник белка, бекон содержит жиры и соль. Блюдо имеет нейтральную кислотность.",
  "recommendations": ["Прополощите рот после еды", "Подождите 30 минут перед чисткой зубов"]
}}

Верни только JSON без дополнительного текста."""

            # Используем Vision API
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            },
                        },
                    ],
                },
            ]

            logger.info(f"Calling Vision API for image analysis: {image_path}")

            # Используем переопределенную модель, если указана, иначе используем базовую модель
            if model_override:
                vision_model = model_override
            else:
                # Используем базовую модель для Vision API
                vision_model = self.model_name

            create_params = {
                "model": vision_model,
                "messages": messages,
            }

            # Для Vision API используем max_tokens
            is_new_model = (
                "gpt-5" in self.model_name.lower() or "o1" in self.model_name.lower()
            )
            if is_new_model:
                create_params["max_completion_tokens"] = (
                    4000  # Увеличено для моделей с reasoning
                )
            else:
                create_params["max_tokens"] = 2000
                create_params["temperature"] = 0.7

            response = await self.client.chat.completions.create(**create_params)

            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.info(
                    f"Vision API response received, content length: {len(content) if content else 0}"
                )

                if content:
                    # Логируем полный ответ для отладки
                    logger.info(f"Vision API full response: {content}")

                    try:
                        json_start = content.find("{")
                        json_end = content.rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = content[json_start:json_end]
                            logger.debug(
                                f"Extracted JSON (first 300 chars): {json_str[:300]}"
                            )

                            analysis = json.loads(json_str)

                            # Убеждаемся, что summary присутствует
                            if "summary" not in analysis or not analysis.get("summary"):
                                logger.warning(
                                    "Summary missing in Vision API response, generating fallback"
                                )
                                # Генерируем summary на основе food_items
                                food_items = analysis.get("food_items", [])
                                if food_items:
                                    food_list = ", ".join(food_items[:5])
                                    analysis["summary"] = (
                                        f"На изображении обнаружено: {food_list}. "
                                    )
                                    if analysis.get("sugar_content", 0) > 20:
                                        analysis[
                                            "summary"
                                        ] += "Высокое содержание сахара. "
                                    if analysis.get("acidity_level", 7.0) < 5.5:
                                        analysis[
                                            "summary"
                                        ] += "Кислая пища может повлиять на эмаль. "
                                    analysis[
                                        "summary"
                                    ] += "Рекомендуется прополоскать рот после еды."
                                else:
                                    analysis["summary"] = (
                                        "Проанализировано изображение еды. Рекомендуется соблюдать гигиену полости рта после приема пищи."
                                    )

                            logger.info(
                                f"Image analysis completed: {len(analysis.get('food_items', []))} items found, summary: {bool(analysis.get('summary'))}"
                            )
                            return analysis
                        else:
                            logger.warning(
                                f"Could not find JSON in response. json_start={json_start}, json_end={json_end}"
                            )
                            logger.warning(f"Full content: {content}")

                            # Проверяем, не отказался ли API анализировать изображение
                            if (
                                "can't help" in content.lower()
                                or "sorry" in content.lower()
                                or "cannot" in content.lower()
                            ):
                                logger.warning(
                                    "Vision API refused to analyze image, using text-based fallback"
                                )
                                # Используем текстовый анализ как fallback
                                fallback_description = (
                                    food_description or "еда на изображении"
                                )
                                logger.info(
                                    f"Falling back to text analysis with description: {fallback_description}"
                                )
                                return await self._analyze_food_text(
                                    fallback_description
                                )

                            # Попробуем извлечь информацию из текста и создать анализ
                            logger.info(
                                "Attempting to extract information from text response"
                            )
                            import re

                            # Пытаемся найти упоминания продуктов и чисел
                            food_keywords = [
                                "яйцо",
                                "яйца",
                                "бекон",
                                "омлет",
                                "яблоко",
                                "кофе",
                                "чай",
                                "мясо",
                                "хлеб",
                                "сыр",
                                "молоко",
                                "сахар",
                                "соль",
                                "масло",
                                "макароны",
                                "паста",
                                "рис",
                                "картофель",
                                "овощи",
                                "фрукты",
                            ]
                            found_foods = []
                            for keyword in food_keywords:
                                if keyword.lower() in content.lower():
                                    found_foods.append(keyword)

                            # Пытаемся найти числа (калории, сахар)
                            numbers = re.findall(r"\d+\.?\d*", content)

                            # Создаем анализ из текста
                            summary_text = (
                                content
                                if len(content) <= 500
                                else content[:500] + "..."
                            )
                            if not found_foods:
                                summary_text = "Проанализировано изображение еды. Рекомендуется соблюдать гигиену полости рта после приема пищи."

                            fallback_analysis = {
                                "food_items": (
                                    found_foods
                                    if found_foods
                                    else ["еда на изображении"]
                                ),
                                "summary": summary_text,
                                "sugar_content": (
                                    float(numbers[0])
                                    if numbers and len(numbers) > 0
                                    else 0.0
                                ),
                                "acidity_level": 7.0,
                                "health_score": 5.0,
                                "calories": (
                                    float(numbers[1])
                                    if numbers and len(numbers) > 1
                                    else 150.0
                                ),
                                "recommendations": [
                                    "Проанализировано изображение. Рекомендуется соблюдать гигиену полости рта после приема пищи."
                                ],
                            }
                            logger.info(
                                f"Created fallback analysis from text response: {len(found_foods)} foods found"
                            )
                            return fallback_analysis

                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Failed to parse Vision API response as JSON: {e}"
                        )
                        logger.warning(f"Response was: {content}")

                        # Создаем анализ из текста даже при ошибке парсинга
                        import re

                        food_keywords = [
                            "яйцо",
                            "яйца",
                            "бекон",
                            "омлет",
                            "яблоко",
                            "кофе",
                            "чай",
                            "мясо",
                            "хлеб",
                            "сыр",
                            "молоко",
                        ]
                        found_foods = [
                            kw for kw in food_keywords if kw.lower() in content.lower()
                        ]

                        fallback_analysis = {
                            "food_items": (
                                found_foods if found_foods else ["еда на изображении"]
                            ),
                            "summary": (
                                content
                                if len(content) <= 500
                                else content[:500] + "..."
                            ),
                            "sugar_content": 0.0,
                            "acidity_level": 7.0,
                            "health_score": 5.0,
                            "calories": 150.0,
                            "recommendations": [
                                "Проанализировано изображение. Рекомендуется соблюдать гигиену полости рта."
                            ],
                        }
                        logger.info("Created fallback analysis after JSON decode error")
                        return fallback_analysis
                else:
                    logger.warning("Vision API returned empty content")

            # Fallback
            logger.warning("Vision API returned empty response, using fallback")
            return await self._analyze_food_text(
                food_description or "еда на изображении"
            )

        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return await self._analyze_food_text(
                food_description or "еда на изображении"
            )
        except Exception as e:
            logger.error(f"Error in image nutrition analysis: {e}", exc_info=True)
            return await self._analyze_food_text(
                food_description or "еда на изображении"
            )

    async def get_psychology_response(self, user_message: str) -> str:
        """Get psychology support response using AI"""
        try:
            # Проверяем что клиент инициализирован
            if not self.client:
                logger.warning("AI client not initialized, using fallback")
                return self._get_fallback_psychology_response(user_message)

            system_prompt = """Ты - профессиональный психологический помощник для людей, которые боятся стоматолога или испытывают тревогу перед визитом к стоматологу.

КРИТИЧЕСКИ ВАЖНО:
- ВСЕГДА отвечай именно на конкретный вопрос или сообщение пользователя
- НЕ используй шаблонные ответы
- Анализируй что именно написал пользователь и отвечай на это
- Если пользователь задал вопрос - отвечай на вопрос
- Если пользователь описал ситуацию - дай совет по этой ситуации
- Будь конкретным и персонализированным

Твоя роль:
- Поддержать человека, успокоить его, дать полезные советы и мотивацию
- Помочь справиться со страхом перед стоматологическими процедурами
- Объяснить, что современная стоматология безопасна и безболезненна
- Дать практические советы по снижению тревоги

Стиль общения:
- Дружелюбный, эмпатичный, понимающий
- На русском языке
- Конкретный и полезный
- Длина ответа: 2-4 предложения
- Не используй медицинские термины без объяснения
- Фокусируйся на поддержке и практических советах

Важно:
- Не давай медицинские диагнозы
- Не заменяй консультацию стоматолога
- Поддерживай и мотивируй"""

            user_prompt = f"""Пользователь написал: "{user_message}"

ОБЯЗАТЕЛЬНО: Проанализируй это сообщение и дай персонализированный ответ, который напрямую относится к тому, что написал пользователь. Если это вопрос - ответь на вопрос. Если это описание ситуации - дай совет по этой ситуации. НЕ используй общие шаблонные фразы."""

            logger.info(f"Calling AI API with message: {user_message[:100]}...")
            # Use gpt-4o for psychology chat (gpt-5-nano is not available in all regions)
            response = await self._call_ai_api(
                system_prompt, user_prompt, model_override="gpt-4o"
            )

            if response and response.strip():
                logger.info(f"AI API returned response: {response[:100]}...")
                return response.strip()
            else:
                logger.warning("AI API returned empty response, using fallback")
                return self._get_fallback_psychology_response(user_message)

        except Exception as e:
            logger.error(f"Error in psychology response: {e}", exc_info=True)
            return self._get_fallback_psychology_response(user_message)

    def _get_default_risks(self) -> Dict[str, float]:
        """Get default risk values"""
        return {
            "cavity_risk": 0.5,
            "gum_disease_risk": 0.5,
            "sensitivity_risk": 0.5,
            "enamel_erosion_risk": 0.5,
        }

    async def _analyze_food_text(self, description: str) -> Dict[str, Any]:
        """Fallback food analysis"""
        # Генерируем summary на основе описания
        food_words = description.split()[:5]
        food_list = ", ".join(food_words)
        summary = f"Проанализировано блюдо: {food_list}. Рекомендуется соблюдать гигиену полости рта после приема пищи."

        return {
            "food_items": description.split(),
            "calories": 150,
            "sugar_content": 20,
            "acidity_level": 5.0,
            "health_score": 7.0,
            "summary": summary,
            "recommendations": [
                "Прополощите рот после еды",
                "Подождите 30 минут перед чисткой зубов",
            ],
        }

    def _get_default_nutrition(self) -> Dict[str, Any]:
        """Get default nutrition analysis"""
        return {
            "food_items": ["неизвестно"],
            "calories": 0,
            "sugar_content": 0,
            "acidity_level": 7.0,
            "health_score": 5.0,
            "summary": "Не удалось провести анализ еды. Попробуйте описать блюдо более подробно или отправьте фото лучшего качества.",
            "recommendations": [
                "Не удалось проанализировать. Попробуйте описать более подробно."
            ],
        }

    def _get_fallback_psychology_response(self, message: str) -> str:
        """Fallback psychology response"""
        message_lower = message.lower()

        if any(
            word in message_lower for word in ["страх", "боюсь", "страшно", "тревога"]
        ):
            return "Понимаю, что вы чувствуете тревогу перед визитом к стоматологу. Это совершенно нормально! Современная стоматология использует эффективные методы обезболивания, и большинство процедур проходят безболезненно."

        if any(word in message_lower for word in ["боль", "болит", "болезненно"]):
            return "Я понимаю ваше беспокойство о боли. Современные анестетики делают лечение практически безболезненным. Если у вас есть вопросы о процедуре, не стесняйтесь задавать их стоматологу."

        return "Я здесь, чтобы поддержать вас. Если у вас есть какие-либо опасения по поводу стоматологического лечения, я готов помочь."

    async def get_braces_response(self, user_message: str) -> str:
        """Get AI response for braces-related questions"""
        try:
            system_prompt = """Ты - эксперт-ортодонт, который помогает людям с брекет-системами.
Твоя задача - отвечать на вопросы о брекетах, давать практические советы и поддержку.

Стиль ответа:
- Дружелюбный, понятный, практичный
- На русском языке
- Конкретный и полезный
- Длина ответа: 2-4 предложения
- Фокусируйся на практических советах

Важно:
- Не давай медицинские диагнозы
- Не заменяй консультацию ортодонта
- Если ситуация серьезная (отклеился брекет, сильная боль), рекомендовай обратиться к врачу"""

            user_prompt = f"""Пользователь написал: "{user_message}"

ОБЯЗАТЕЛЬНО: Проанализируй это сообщение и дай персонализированный ответ, который напрямую относится к тому, что написал пользователь. Если это вопрос - ответь на вопрос. Если это описание ситуации - дай совет по этой ситуации. НЕ используй общие шаблонные фразы."""

            logger.info(f"Calling AI API for braces question: {user_message[:100]}...")
            response = await self._call_ai_api(system_prompt, user_prompt)

            if response and response.strip():
                logger.info(f"AI API returned braces response: {response[:100]}...")
                return response.strip()
            else:
                logger.warning("AI API returned empty response, using fallback")
                return self._get_fallback_braces_response(user_message)

        except Exception as e:
            logger.error(f"Error in braces response: {e}", exc_info=True)
            return self._get_fallback_braces_response(user_message)

    def _get_fallback_braces_response(self, message: str) -> str:
        """Fallback braces response"""
        message_lower = message.lower()

        if any(
            word in message_lower
            for word in ["боль", "болит", "болезненно", "дискомфорт"]
        ):
            return "При боли от брекетов попробуйте: 1) Принять обезболивающее по назначению врача, 2) Приложить холод к щеке, 3) Есть мягкую пищу. Боль обычно проходит через 3-5 дней."

        if any(
            word in message_lower for word in ["еда", "питание", "кушать", "можно ли"]
        ):
            return "С брекетами можно есть мягкую пищу: йогурты, супы, каши. Избегайте твердых, липких продуктов. Нарежьте твердые овощи и фрукты на мелкие кусочки."

        if any(
            word in message_lower
            for word in ["чистка", "гигиена", "зубная щетка", "нить"]
        ):
            return "Чистите брекеты мягкой щеткой и специальной щеткой для брекетов. Чистите каждый зуб и брекет отдельно. Используйте зубную нить и ирригатор."

        if any(
            word in message_lower
            for word in ["отклеился", "отвалился", "сломался", "оторвался"]
        ):
            return "Если отклеился брекет, немедленно обратитесь к ортодонту. Не пытайтесь приклеить его самостоятельно. Сохраните брекет и принесите на прием."

        return "Я помогу вам с вопросами о брекетах. Опишите вашу проблему более подробно, и я дам конкретные советы."
