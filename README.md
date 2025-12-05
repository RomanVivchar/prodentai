# ProDentAI

Комплексная система для проактивного поддержания стоматологического здоровья.

## Структура проекта

- `backend/` - FastAPI backend
- `telegram_bot/` - Telegram бот
- `web/` - React frontend
- `shared/` - Общие модули (ML сервисы)
- `nginx/` - Nginx конфигурация

## Запуск

### Development

```bash
docker-compose up
```

### Production

См. `DEPLOYMENT.md` для инструкций по деплою.

## Переменные окружения

Создайте `.env` файл на основе `env.example`:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=prodentai
OPENAI_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
ALLOWED_ORIGINS=https://prodentai.tech,http://prodentai.tech
REACT_APP_API_URL=https://prodentai.tech/api
```

## API

Backend доступен на `http://localhost:8000`
API документация: `http://localhost:8000/docs`

## Домен

Production: https://prodentai.tech

