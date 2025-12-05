"""
Facts router
"""

import random

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import BracesFAQ, Fact, User
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Default facts database (used when database is empty)
DEFAULT_FACTS = [
    # Гигиена (hygiene)
    {
        "id": 1,
        "title": "Электрические зубные щетки",
        "content": "Электрические зубные щетки удаляют налет эффективнее ручных благодаря стабильным движениям.",
        "category": "hygiene",
    },
    {
        "id": 2,
        "title": "Время чистки зубов",
        "content": "Большинство людей чистят зубы всего 45–60 секунд, хотя рекомендуется около 2 минут.",
        "category": "hygiene",
    },
    {
        "id": 3,
        "title": "Мягкая щетка",
        "content": "Мягкая щетка очищает так же эффективно, как жесткая, но меньше травмирует десны.",
        "category": "hygiene",
    },
    {
        "id": 4,
        "title": "Смена зубной щетки",
        "content": "Смена зубной щетки каждые 2–3 месяца снижает риск накопления бактерий.",
        "category": "hygiene",
    },
    {
        "id": 5,
        "title": "Чистка языка",
        "content": "Язык — одно из самых «бактериальных» мест во рту, и его регулярная чистка уменьшает запах.",
        "category": "hygiene",
    },
    {
        "id": 6,
        "title": "Полоскание после чистки",
        "content": "Полоскание рта сразу после чистки может снижать эффект фторсодержащей пасты.",
        "category": "hygiene",
    },
    {
        "id": 7,
        "title": "Количество зубной пасты",
        "content": "Зубная паста не нужна в большом количестве — достаточно объема с горошину.",
        "category": "hygiene",
    },
    {
        "id": 8,
        "title": "Использование нити",
        "content": "Использование нити перед чисткой помогает проникнуть фтору в межзубные пространства.",
        "category": "hygiene",
    },
    {
        "id": 9,
        "title": "Правильное использование нити",
        "content": "Большинство людей используют нить неправильно — слишком резко, травмируя десны.",
        "category": "hygiene",
    },
    {
        "id": 10,
        "title": "Щетки с изогнутой щетиной",
        "content": "Щетки с изогнутой щетиной лучше проникают в труднодоступные участки.",
        "category": "hygiene",
    },
    {
        "id": 11,
        "title": "Отбеливающие пасты",
        "content": "Отбеливающие пасты чаще всего работают за счёт абразивов, а не химии.",
        "category": "hygiene",
    },
    {
        "id": 12,
        "title": "Образование зубного налета",
        "content": "Зубной налет начинает образовываться уже через 4–12 часов после чистки.",
        "category": "hygiene",
    },
    {
        "id": 13,
        "title": "Полоскатель для рта",
        "content": "Полоскатель для рта не заменяет щетку и нить, а только дополняет их.",
        "category": "hygiene",
    },
    {
        "id": 14,
        "title": "Давление при чистке",
        "content": "Слишком сильное давление щеткой может стирать эмаль на шейке зуба.",
        "category": "hygiene",
    },
    {
        "id": 15,
        "title": "Чистка перед сном",
        "content": "Чистка зубов перед сном — самая важная, так как ночью слюна почти не выделяется.",
        "category": "hygiene",
    },
    # Питание (nutrition)
    {
        "id": 16,
        "title": "Кислые напитки",
        "content": "Кислые напитки (например, кола) могут размягчать эмаль, даже если в них нет сахара.",
        "category": "nutrition",
    },
    {
        "id": 17,
        "title": "Сыры твердых сортов",
        "content": "Сыры твердых сортов помогают нейтрализовать кислотность во рту.",
        "category": "nutrition",
    },
    {
        "id": 18,
        "title": "Хрустящие овощи",
        "content": "Хрустящие овощи вроде моркови механически очищают зубы.",
        "category": "nutrition",
    },
    {
        "id": 19,
        "title": "Частые перекусы",
        "content": "Слишком частые перекусы вреднее, чем большой прием пищи — они постоянно поднимают уровень кислотности.",
        "category": "nutrition",
    },
    {
        "id": 20,
        "title": "Кислоты во фруктах",
        "content": "Фрукты полезны, но их кислоты могут временно ослаблять эмаль.",
        "category": "nutrition",
    },
    {
        "id": 21,
        "title": "Липкие сладости",
        "content": "Сладости липкой текстуры (карамель, ириски) дольше удерживаются на зубах.",
        "category": "nutrition",
    },
    {
        "id": 22,
        "title": "Натуральные соки",
        "content": "Натуральные соки по кислотности могут быть сопоставимы с газировкой.",
        "category": "nutrition",
    },
    {
        "id": 23,
        "title": "Орехи и минералы",
        "content": "Орехи содержат минералы, которые участвуют в укреплении эмали.",
        "category": "nutrition",
    },
    {
        "id": 24,
        "title": "Сахар перед сном",
        "content": "Отказ от сахара перед сном особенно важен — ночью слюна не «отмывает» зубы.",
        "category": "nutrition",
    },
    {
        "id": 25,
        "title": "Хлеб и булки",
        "content": "Хлеб и булки превращаются в сахара уже при расщеплении слюной.",
        "category": "nutrition",
    },
    {
        "id": 26,
        "title": "Вода после еды",
        "content": "Вода — лучший напиток для нейтрализации кислот после еды.",
        "category": "nutrition",
    },
    {
        "id": 27,
        "title": "Зеленый чай",
        "content": "Зеленый чай содержит катехины, которые уменьшают рост бактерий.",
        "category": "nutrition",
    },
    {
        "id": 28,
        "title": "Белок для десен",
        "content": "Белок — важный компонент для восстановления тканей десны.",
        "category": "nutrition",
    },
    {
        "id": 29,
        "title": "Темные ягоды",
        "content": "Темные ягоды могут окрашивать эмаль, а светлые — нет.",
        "category": "nutrition",
    },
    {
        "id": 30,
        "title": "Молочные продукты",
        "content": "Молочные продукты содержат кальций, необходимый для зубов.",
        "category": "nutrition",
    },
    # Профилактика (prevention)
    {
        "id": 31,
        "title": "Регулярные визиты к стоматологу",
        "content": "Регулярные визиты к стоматологу каждые 6 месяцев помогают выявлять скрытые проблемы.",
        "category": "prevention",
    },
    {
        "id": 32,
        "title": "Фторирование",
        "content": "Фторирование укрепляет эмаль, особенно у людей с тонкой эмалью.",
        "category": "prevention",
    },
    {
        "id": 33,
        "title": "Защитные каппы",
        "content": "Защитные каппы предотвращают стираемость зубов при бруксизме.",
        "category": "prevention",
    },
    {
        "id": 34,
        "title": "Вода после еды",
        "content": "Питьё воды после еды снижает риск кариеса.",
        "category": "prevention",
    },
    {
        "id": 35,
        "title": "Избегание перекусов",
        "content": "Избегание перекусов уменьшает кислотные атаки на эмаль.",
        "category": "prevention",
    },
    {
        "id": 36,
        "title": "Уход за деснами",
        "content": "Уход за деснами важен не меньше, чем уход за зубами.",
        "category": "prevention",
    },
    {
        "id": 37,
        "title": "Ортодонтические проблемы",
        "content": "Ортодонтические проблемы повышают риск кариеса из-за труднодоступных зон.",
        "category": "prevention",
    },
    {
        "id": 38,
        "title": "Курение и десны",
        "content": "Курение ухудшает кровоснабжение десен и замедляет заживление.",
        "category": "prevention",
    },
    {
        "id": 39,
        "title": "Неправильный прикус",
        "content": "Неправильный прикус может вести к повышенной нагрузке на отдельные зубы.",
        "category": "prevention",
    },
    {
        "id": 40,
        "title": "Детские зубы",
        "content": "Детские зубы нуждаются в профилактике так же, как и постоянные.",
        "category": "prevention",
    },
    {
        "id": 41,
        "title": "Ирригатор",
        "content": "Пользование ирригатором помогает очищать участки под десной.",
        "category": "prevention",
    },
    {
        "id": 42,
        "title": "Витамин D",
        "content": "Прием витамина D поддерживает здоровье костной ткани.",
        "category": "prevention",
    },
    {
        "id": 43,
        "title": "Замена пломб",
        "content": "Своевременная замена старых пломб предотвращает вторичный кариес.",
        "category": "prevention",
    },
    {
        "id": 44,
        "title": "Спортивные каппы",
        "content": "Спортивные каппы защищают зубы от ударов.",
        "category": "prevention",
    },
    {
        "id": 45,
        "title": "Чистка после кислой еды",
        "content": "Не рекомендуется чистить зубы сразу после кислой еды — эмаль временно размягчена.",
        "category": "prevention",
    },
    # История (history)
    {
        "id": 46,
        "title": "Первые зубные щетки",
        "content": "Первые зубные щетки появились в Китае в XV веке и делались из щетины кабана.",
        "category": "history",
    },
    {
        "id": 47,
        "title": "Древнеегипетские пасты",
        "content": "В Древнем Египте зубные пасты создавали из пемзы и золы.",
        "category": "history",
    },
    {
        "id": 48,
        "title": "Древние пломбы",
        "content": "Археологи находили примитивные пломбы из пчелиного воска у людей возрастом более 6000 лет.",
        "category": "history",
    },
    {
        "id": 49,
        "title": "Средневековые цирюльники",
        "content": "В Средневековье зубы иногда удаляли цирюльники, а не врачи.",
        "category": "history",
    },
    {
        "id": 50,
        "title": "Зубная боль в античности",
        "content": "Зубная боль была одним из самых частых поводов обратиться к врачу в античности.",
        "category": "history",
    },
    {
        "id": 51,
        "title": "Металлические пломбы",
        "content": "Первые металлические пломбы появились в Японии несколько столетий назад.",
        "category": "history",
    },
    {
        "id": 52,
        "title": "Зубной червь",
        "content": "Зубной червь — популярное древнее объяснение кариеса, встречалось даже в Месопотамии.",
        "category": "history",
    },
    {
        "id": 53,
        "title": "Фарфоровые протезы",
        "content": "В XIX веке зубные протезы часто делали из фарфора.",
        "category": "history",
    },
    {
        "id": 54,
        "title": "Первый электрический бор",
        "content": "Первый электрический бор был изобретён в 1875 году.",
        "category": "history",
    },
    {
        "id": 55,
        "title": "Средневековые рецепты паст",
        "content": "Средневековые рецепты паст включали мёд, яйца и измельченные кости.",
        "category": "history",
    },
    {
        "id": 56,
        "title": "Древнеримские стоматологи",
        "content": "В Древнем Риме существовали профессиональные стоматологи.",
        "category": "history",
    },
    {
        "id": 57,
        "title": "Первые зубные нити",
        "content": "Первые зубные нити делали из шелка.",
        "category": "history",
    },
    {
        "id": 58,
        "title": "Новокаин в стоматологии",
        "content": "В 1905 году впервые применили новокаин в стоматологии.",
        "category": "history",
    },
    {
        "id": 59,
        "title": "Магия и заговоры",
        "content": "В прошлом считалось, что зубы можно лечить магией и заговорами.",
        "category": "history",
    },
    {
        "id": 60,
        "title": "Удаление без анестезии",
        "content": "До появления анестезии удаление зубов было одним из самых болезненных вмешательств в медицине.",
        "category": "history",
    },
]


class FactResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str

    class Config:
        from_attributes = True


class BracesFAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str

    class Config:
        from_attributes = True


@router.get("/random", response_model=FactResponse)
async def get_random_fact(db: AsyncSession = Depends(get_db)):
    """Get random hygiene fact"""
    result = await db.execute(select(Fact).where(Fact.is_active))
    facts = result.scalars().all()

    if not facts:
        # Return random default fact if no facts in database
        fact_data = random.choice(DEFAULT_FACTS)
        return FactResponse(
            id=fact_data["id"],
            title=fact_data["title"],
            content=fact_data["content"],
            category=fact_data["category"],
        )

    fact = random.choice(facts)
    return FactResponse(
        id=fact.id, title=fact.title, content=fact.content, category=fact.category
    )


@router.get("/category/{category}")
async def get_facts_by_category(category: str, db: AsyncSession = Depends(get_db)):
    """Get facts by category"""
    result = await db.execute(
        select(Fact).where(Fact.category == category, Fact.is_active)
    )
    facts = result.scalars().all()

    # If no facts in database, use default facts
    if not facts:
        default_facts = [f for f in DEFAULT_FACTS if f["category"] == category]
        return [
            {
                "id": fact["id"],
                "title": fact["title"],
                "content": fact["content"],
                "category": fact["category"],
            }
            for fact in default_facts
        ]

    return [
        {
            "id": fact.id,
            "title": fact.title,
            "content": fact.content,
            "category": fact.category,
        }
        for fact in facts
    ]


@router.get("/categories")
async def get_fact_categories():
    """Get available fact categories"""
    categories = [
        {
            "name": "hygiene",
            "title": "Гигиена",
            "description": "Факты о правильной гигиене полости рта",
        },
        {
            "name": "nutrition",
            "title": "Питание",
            "description": "Влияние питания на здоровье зубов",
        },
        {
            "name": "prevention",
            "title": "Профилактика",
            "description": "Способы предотвращения стоматологических проблем",
        },
        {
            "name": "history",
            "title": "История",
            "description": "Интересные исторические факты о стоматологии",
        },
    ]

    return {"categories": categories}


@router.get("/braces/search")
async def search_braces_faq(query: str, db: AsyncSession = Depends(get_db)):
    """Search braces FAQ by query"""
    # Simple keyword search
    result = await db.execute(select(BracesFAQ).where(BracesFAQ.is_active))
    faqs = result.scalars().all()

    # Filter by keywords (simple implementation)
    matching_faqs = []
    query_lower = query.lower()

    for faq in faqs:
        if (
            query_lower in faq.question.lower()
            or query_lower in faq.answer.lower()
            or any(keyword.lower() in query_lower for keyword in faq.keywords or [])
        ):
            matching_faqs.append(faq)

    return [
        {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "category": faq.category,
        }
        for faq in matching_faqs
    ]


@router.get("/braces/category/{category}")
async def get_braces_faq_by_category(category: str, db: AsyncSession = Depends(get_db)):
    """Get braces FAQ by category"""
    result = await db.execute(
        select(BracesFAQ).where(BracesFAQ.category == category, BracesFAQ.is_active)
    )
    faqs = result.scalars().all()

    return [
        {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "category": faq.category,
        }
        for faq in faqs
    ]


@router.get("/braces/categories")
async def get_braces_categories():
    """Get braces FAQ categories"""
    categories = [
        {
            "name": "pain",
            "title": "Боль и дискомфорт",
            "description": "Вопросы о боли и дискомфорте от брекетов",
        },
        {
            "name": "food",
            "title": "Питание",
            "description": "Что можно и нельзя есть с брекетами",
        },
        {
            "name": "cleaning",
            "title": "Чистка",
            "description": "Как правильно чистить брекеты",
        },
        {
            "name": "emergency",
            "title": "Экстренные ситуации",
            "description": "Что делать в экстренных случаях",
        },
    ]

    return {"categories": categories}


class BracesChatRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    message: str = Field(..., min_length=1, max_length=1000, description="User message")


class BracesChatResponse(BaseModel):
    response: str


@router.post("/braces/chat", response_model=BracesChatResponse)
async def braces_chat(request: BracesChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat with AI assistant about braces"""
    # Check if user exists
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Используем AI API через MLServiceManager
    import logging

    from main import ml_manager

    logger = logging.getLogger(__name__)

    try:
        # Получаем ответ от AI
        logger.info(f"Calling AI API for braces message: {request.message[:50]}...")
        ai_response = await ml_manager.get_braces_response(request.message)
        logger.info(
            f"AI response received: {ai_response[:100] if ai_response else 'Empty'}..."
        )

        # Если AI не вернул ответ, используем fallback
        if not ai_response or len(ai_response.strip()) == 0:
            ai_response = "Я помогу вам с вопросами о брекетах. Опишите вашу проблему более подробно, и я дам конкретные советы."

    except Exception as e:
        # Логируем ошибку для отладки
        logger.error(f"Error calling AI API: {e}", exc_info=True)
        # Fallback на простые ответы при ошибке AI
        message_lower = request.message.lower()
        if any(word in message_lower for word in ["боль", "болит", "болезненно"]):
            ai_response = "При боли от брекетов попробуйте: 1) Принять обезболивающее по назначению врача, 2) Приложить холод к щеке, 3) Есть мягкую пищу. Боль обычно проходит через 3-5 дней."
        elif any(word in message_lower for word in ["еда", "питание", "кушать"]):
            ai_response = "С брекетами можно есть мягкую пищу: йогурты, супы, каши. Избегайте твердых, липких продуктов."
        elif any(word in message_lower for word in ["чистка", "гигиена"]):
            ai_response = "Чистите брекеты мягкой щеткой и специальной щеткой для брекетов. Чистите каждый зуб и брекет отдельно."
        elif any(word in message_lower for word in ["отклеился", "отвалился"]):
            ai_response = "Если отклеился брекет, немедленно обратитесь к ортодонту. Не пытайтесь приклеить его самостоятельно."
        else:
            ai_response = "Я помогу вам с вопросами о брекетах. Опишите вашу проблему более подробно, и я дам конкретные советы."

    return BracesChatResponse(response=ai_response)
