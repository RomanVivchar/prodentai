# Исправление ошибок Docker Compose

## 🔴 Критические ошибки (исправлены)

### 1. Backend: AttributeError с OAuth2PasswordRequestForm
**Ошибка:**
```
AttributeError: 'FieldInfo' object has no attribute 'in_'
```

**Причина:** Несовместимость версий FastAPI 0.104.1 с Pydantic v2

**Решение:**
- ✅ Обновлен FastAPI до 0.115.0
- ✅ Добавлен явный pydantic>=2.0.0,<3.0.0
- ✅ Добавлен pydantic-settings>=2.0.0

### 2. Frontend: Отсутствующие файлы
**Ошибка:**
```
Module not found: Error: Can't resolve './pages/Login'
```

**Решение:**
- ✅ Создан `web/src/pages/Login.tsx`
- ✅ Создан `web/src/pages/Register.tsx`
- ✅ Создан `web/src/pages/Profile.tsx`

### 3. Nginx: SSL сертификаты не найдены
**Ошибка:**
```
cannot load certificate "/etc/letsencrypt/live/prodentai.tech/fullchain.pem"
```

**Решение:**
- ✅ Создан `nginx/nginx.conf.dev` для разработки без SSL
- ✅ `docker-compose.yml` настроен на использование `nginx.conf.dev`
- ✅ Для продакшена можно переключиться на `nginx.conf`

### 4. Nginx: Deprecated http2 синтаксис
**Предупреждение:**
```
the "listen ... http2" directive is deprecated
```

**Решение:**
- ✅ Исправлен синтаксис в `nginx.conf`:
  ```nginx
  listen 443 ssl;
  http2 on;
  ```

## 📝 Изменения в файлах

### backend/requirements.txt
```diff
- fastapi==0.104.1
+ fastapi==0.115.0
+ pydantic>=2.0.0,<3.0.0
+ pydantic-settings>=2.0.0
```

### docker-compose.yml
```diff
- - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
+ - ./nginx/nginx.conf.dev:/etc/nginx/nginx.conf:ro
```

### Новые файлы
- `nginx/nginx.conf.dev` - конфигурация для разработки
- `web/src/pages/Login.tsx`
- `web/src/pages/Register.tsx`
- `web/src/pages/Profile.tsx`

## 🚀 Запуск после исправлений

```bash
# Пересобрать образы с новыми зависимостями
docker-compose build

# Запустить все сервисы
docker-compose up -d

# Проверить логи
docker-compose logs -f
```

## ⚠️ Для продакшена

Перед развертыванием на prodentai.tech:

1. **Получите SSL сертификаты:**
   ```bash
   certbot certonly --standalone -d prodentai.tech -d www.prodentai.tech
   ```

2. **Измените docker-compose.yml:**
   ```yaml
   volumes:
     - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro  # Используйте продакшен конфиг
     - /etc/letsencrypt:/etc/letsencrypt:ro  # Раскомментируйте
   ```

3. **Перезапустите nginx:**
   ```bash
   docker-compose restart nginx
   ```

## ✅ Статус

Все критические ошибки исправлены:
- ✅ Backend должен запускаться
- ✅ Frontend должен собираться
- ✅ Nginx должен работать (без SSL для разработки)
- ✅ Все необходимые файлы созданы

