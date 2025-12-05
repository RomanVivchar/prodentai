# ✅ Чеклист развертывания на prodentai.tech

## 🔧 Предварительная настройка

### 1. Сервер
- [ ] Установлен Docker и Docker Compose
- [ ] Домен `prodentai.tech` указывает на IP сервера
- [ ] Порты 80 и 443 открыты в firewall

### 2. SSL сертификаты
- [ ] Получены сертификаты Let's Encrypt для `prodentai.tech` и `www.prodentai.tech`
- [ ] Сертификаты размещены в `/etc/letsencrypt/live/prodentai.tech/`
- [ ] Права доступа настроены (nginx должен читать сертификаты)

### 3. Переменные окружения
Создайте `.env` файл на сервере:
```bash
# Security (ОБЯЗАТЕЛЬНО измените!)
SECRET_KEY=your-very-secure-random-secret-key-min-32-chars

# Database
POSTGRES_DB=prodentai
POSTGRES_USER=prodentai
POSTGRES_PASSWORD=your-secure-database-password

# Redis (в Docker автоматически redis://redis:6379)
# Не нужно указывать, но можно для ясности:
REDIS_URL=redis://redis:6379

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_MODEL=gpt-3.5-turbo

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# CORS (уже правильно в docker-compose, но можно переопределить)
ALLOWED_ORIGINS=https://prodentai.tech,http://prodentai.tech

# Frontend (автоматически в docker-compose)
REACT_APP_API_URL=https://prodentai.tech/api
```

## 🚀 Развертывание

### Шаг 1: Клонирование проекта
```bash
git clone <your-repo-url>
cd ProDentAI
```

### Шаг 2: Создание .env файла
```bash
nano .env
# Вставьте переменные окружения из раздела выше
```

### Шаг 3: Получение SSL сертификатов (если еще нет)
```bash
# Остановите nginx временно
docker-compose stop nginx

# Получите сертификаты
certbot certonly --standalone -d prodentai.tech -d www.prodentai.tech

# Запустите nginx обратно
docker-compose start nginx
```

### Шаг 4: Сборка и запуск
```bash
# Сборка всех образов
docker-compose build

# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### Шаг 5: Проверка логов
```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs backend
docker-compose logs nginx
docker-compose logs telegram_bot
```

## ✅ Проверка работоспособности

### 1. Health Check
```bash
curl https://prodentai.tech/api/health
```
Ожидаемый ответ:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "ml_service": "initialized"
}
```

### 2. API документация
Откройте в браузере:
- https://prodentai.tech/api/docs
- https://prodentai.tech/api/redoc

### 3. Фронтенд
Откройте в браузере:
- https://prodentai.tech

### 4. Проверка SSL
```bash
curl -I https://prodentai.tech
# Должен вернуть 200 OK и показать SSL сертификат
```

## 🔍 Мониторинг

### Просмотр логов в реальном времени
```bash
docker-compose logs -f
```

### Проверка использования ресурсов
```bash
docker stats
```

### Перезапуск сервисов
```bash
# Все сервисы
docker-compose restart

# Конкретный сервис
docker-compose restart backend
docker-compose restart nginx
```

## 🔄 Обновление

### Обновление кода
```bash
git pull
docker-compose build
docker-compose up -d
```

### Обновление только фронтенда
```bash
docker-compose build frontend
docker-compose up -d frontend
```

## ⚠️ Важные замечания

1. **SECRET_KEY** - ОБЯЗАТЕЛЬНО измените на уникальный случайный ключ!
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Пароли БД** - Используйте сложные пароли

3. **.env файл** - НИКОГДА не коммитьте в git!

4. **SSL сертификаты** - Обновляются автоматически certbot, но проверьте настройки автообновления

5. **Бэкапы БД** - Настройте регулярные бэкапы PostgreSQL

## 🐛 Решение проблем

### Проблема: Nginx не запускается
```bash
# Проверьте логи
docker-compose logs nginx

# Проверьте наличие SSL сертификатов
ls -la /etc/letsencrypt/live/prodentai.tech/
```

### Проблема: Backend не подключается к БД
```bash
# Проверьте логи
docker-compose logs backend

# Проверьте переменные окружения
docker-compose exec backend env | grep DATABASE_URL
```

### Проблема: Фронтенд показывает ошибки API
```bash
# Проверьте REACT_APP_API_URL
docker-compose exec frontend env | grep REACT_APP_API_URL

# Должно быть: REACT_APP_API_URL=https://prodentai.tech/api
```

### Проблема: CORS ошибки
```bash
# Проверьте ALLOWED_ORIGINS
docker-compose exec backend env | grep ALLOWED_ORIGINS

# Должно включать: https://prodentai.tech
```

## 📊 Структура URL в продакшене

- **Фронтенд:** https://prodentai.tech
- **API:** https://prodentai.tech/api
- **API Docs:** https://prodentai.tech/api/docs
- **Health Check:** https://prodentai.tech/api/health

## 🔒 Безопасность

- ✅ HTTPS принудительно включен
- ✅ HTTP → HTTPS редирект
- ✅ Security headers в nginx
- ✅ CORS ограничен доменом
- ⚠️ Убедитесь, что `.env` не в git!
- ⚠️ Используйте сложные пароли!
- ⚠️ Регулярно обновляйте зависимости!

