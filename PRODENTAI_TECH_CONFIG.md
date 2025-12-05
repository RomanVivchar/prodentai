# ✅ Конфигурация для prodentai.tech

## 🎯 Текущая настройка

### ✅ Docker Compose
```yaml
# Frontend
REACT_APP_API_URL=https://prodentai.tech/api  # ✅ Правильно

# Backend CORS
ALLOWED_ORIGINS=https://prodentai.tech,http://prodentai.tech  # ✅ Правильно

# Redis (внутри Docker)
REDIS_URL=redis://redis:6379  # ✅ Правильно (имя сервиса)

# Database (внутри Docker)
DATABASE_URL=postgresql://...@postgres:5432/...  # ✅ Правильно (имя сервиса)
```

### ✅ Nginx
```nginx
# Сервер
server_name prodentai.tech www.prodentai.tech;  # ✅ Правильно

# Проксирование API
location /api/ {
    proxy_pass http://backend;  # ✅ Исправлено (без слеша, сохраняет путь)
}

# SSL
ssl_certificate /etc/letsencrypt/live/prodentai.tech/fullchain.pem;  # ✅
```

### ✅ Frontend
Все компоненты используют:
```typescript
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
// В продакшене: https://prodentai.tech/api
```

## 📋 Структура URL

### В продакшене (prodentai.tech):
- **Главная:** https://prodentai.tech
- **API:** https://prodentai.tech/api
- **API Docs:** https://prodentai.tech/api/docs
- **Health:** https://prodentai.tech/api/health

### Как это работает:
1. Пользователь открывает `https://prodentai.tech`
2. Nginx отдает статические файлы React из `/usr/share/nginx/html`
3. React делает запросы к `https://prodentai.tech/api/...`
4. Nginx проксирует `/api/...` → `http://backend:8000/api/...`
5. FastAPI обрабатывает запрос и возвращает ответ

## 🔧 Что было исправлено

1. ✅ **Nginx proxy_pass** - убран слеш в конце (`http://backend/` → `http://backend`)
   - Теперь путь `/api/...` сохраняется при проксировании
   - Запрос `https://prodentai.tech/api/nutrition/analyze` → `http://backend:8000/api/nutrition/analyze`

2. ✅ **Документация** - созданы файлы:
   - `PRODUCTION_CONFIG.md` - общая конфигурация
   - `DEPLOYMENT_CHECKLIST.md` - чеклист развертывания
   - `PRODENTAI_TECH_CONFIG.md` - этот файл

## 🚀 Готово к развертыванию

Все настройки для prodentai.tech готовы:
- ✅ Docker Compose настроен
- ✅ Nginx настроен
- ✅ CORS настроен
- ✅ API URL настроен
- ✅ SSL готов (нужно только установить сертификаты)

## 📝 Следующие шаги

1. Установите SSL сертификаты Let's Encrypt
2. Создайте `.env` файл с переменными окружения
3. Запустите `docker-compose up -d`
4. Проверьте https://prodentai.tech

Подробности в `DEPLOYMENT_CHECKLIST.md`

