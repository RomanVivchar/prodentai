import json
from typing import Any, Dict, List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import PsychologySession, User
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth import get_current_user

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_psychologist(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        from main import ml_manager

        # Get user message (last message in chat)
        user_message = chat_request.messages[-1].content if chat_request.messages else ""
        
        # Get AI response
        response = await ml_manager.get_psychology_response(user_message)

        # Save session
        session = PsychologySession(
            user_id=current_user.id,
            messages=json.dumps(
                [{"role": m.role, "content": m.content} for m in chat_request.messages] 
                + [{"role": "assistant", "content": response}]
            ),
            user_message=user_message,
            ai_response=response,
            session_type="general",
        )
        db.add(session)
        await db.commit()

        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PsychologySession)
        .where(PsychologySession.user_id == current_user.id)
        .order_by(PsychologySession.created_at.desc())
        .limit(10)
    )
    sessions = result.scalars().all()

    return [
        {
            "id": s.id, 
            "messages": json.loads(s.messages) if s.messages else [],
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in sessions
    ]


@router.get("/tips")
async def get_psychology_tips():
    """Get psychology tips for reducing anxiety"""
    tips = [
        {
            "title": "Глубокое дыхание",
            "content": "Практикуйте глубокое дыхание перед визитом. Вдох на 4 счета, задержка на 4, выдох на 4. Это помогает снизить тревогу."
        },
        {
            "title": "Музыка и отвлечение",
            "content": "Слушайте любимую музыку во время процедуры. Это поможет отвлечься и расслабиться."
        },
        {
            "title": "Открытое общение",
            "content": "Расскажите стоматологу о своих страхах. Врач сможет адаптировать подход и объяснить каждый шаг."
        },
        {
            "title": "Начните с малого",
            "content": "Начните с простого осмотра или чистки. Это поможет привыкнуть к обстановке и снизить тревогу."
        },
        {
            "title": "Визуализация",
            "content": "Представьте себя в спокойном месте во время процедуры. Визуализация помогает расслабиться."
        },
        {
            "title": "Сигнал стоп",
            "content": "Договоритесь с врачом о сигнале, которым вы можете остановить процедуру. Это даст чувство контроля."
        }
    ]
    
    return {"tips": tips}
