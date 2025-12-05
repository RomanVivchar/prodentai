# Конфигурация для продакшена prodentai.tech

## ✅ Текущая конфигурация

### Docker Compose
- ✅ `REACT_APP_API_URL=https://prodentai.tech/api` - правильно настроено
- ✅ `ALLOWED_ORIGINS=https://prodentai.tech,http://prodentai.tech` - правильно настроено
- ✅ `REDIS_URL=redis://redis:6379` - правильно (имя сервиса)
- ✅ `DATABASE_URL=postgresql://...@postgres:5432/...` - правильно (имя сервиса)

### Nginx
- ✅ Сервер настроен на `prodentai.tech` и `www.prodentai.tech`
- ✅ HTTPS с Let's Encrypt сертификатами
- ✅ Редирект HTTP → HTTPS
- ✅ Проксирование `/api/` → `backend:8000`
- ✅ Статические файлы фронтенда

### Frontend
- ✅ Использует `process.env.REACT_APP_API_URL` (в Docker = `https://prodentai.tech/api`)
- ✅ Fallback на `localhost:8000` только для локальной разработки

## 🔍 Проверка конфигурации

### 1. API URL в фронтенде
В продакшене фронтенд будет использовать:
```
https://prodentai.tech/api
```

Это правильно, потому что:
- Nginx проксирует `/api/` → `backend:8000`
- FastAPI роутеры имеют префикс `/api/...`
- Итоговый путь: `https://prodentai.tech/api/auth/...`

### 2. CORS настройки
Backend разрешает запросы с:
- `https://prodentai.tech`
- `http://prodentai.tech` (для редиректа)

### 3. SSL сертификаты
Nginx ожидает сертификаты в:
```
/etc/letsencrypt/live/prodentai.tech/fullchain.pem
/etc/letsencrypt/live/prodentai.tech/privkey.pem
```

**Важно:** Убедитесь, что сертификаты установлены на сервере!

## 📝 Переменные окружения для продакшена

Создайте `.env` файл на сервере:

```bash
# Security
SECRET_KEY=your-very-secure-secret-key-here-change-this

# Database
POSTGRES_DB=prodentai
POSTGRES_USER=prodentai
POSTGRES_PASSWORD=your-secure-password-here

# Redis (в Docker автоматически redis://redis:6379)
REDIS_URL=redis://redis:6379

# OpenAI
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-3.5-turbo

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# CORS
ALLOWED_ORIGINS=https://prodentai.tech,http://prodentai.tech

# Frontend (автоматически в Docker)
REACT_APP_API_URL=https://prodentai.tech/api
```

## 🚀 Развертывание

### 1. Подготовка сервера
```bash
# Установите Docker и Docker Compose
# Настройте домен prodentai.tech на IP сервера
# Установите SSL сертификаты Let's Encrypt
```

### 2. Клонирование и настройка
```bash
git clone <your-repo>
cd ProDentAI
# Создайте .env файл с переменными выше
```

### 3. Получение SSL сертификатов
```bash
# Используйте certbot для получения сертификатов
certbot certonly --standalone -d prodentai.tech -d www.prodentai.tech
```

### 4. Запуск
```bash
docker-compose up -d
```

### 5. Проверка
- Откройте https://prodentai.tech
- Проверьте API: https://prodentai.tech/api/health
- Проверьте документацию: https://prodentai.tech/api/docs

## ⚠️ Важные замечания

1. **SSL сертификаты** должны быть установлены до запуска nginx
2. **SECRET_KEY** должен быть уникальным и безопасным
3. **Пароли БД** должны быть сложными
4. **OPENAI_API_KEY** должен быть валидным
5. **TELEGRAM_BOT_TOKEN** должен быть валидным

## 🔒 Безопасность

- ✅ HTTPS принудительно включен
- ✅ Security headers настроены в nginx
- ✅ CORS ограничен доменом prodentai.tech
- ✅ SECRET_KEY из переменных окружения
- ⚠️ Убедитесь, что `.env` файл не попал в git!

## 📊 Мониторинг

После развертывания проверьте:
- Логи: `docker-compose logs -f`
- Health check: `curl https://prodentai.tech/api/health`
- Статус контейнеров: `docker-compose ps`

