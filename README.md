# Metrics API

REST API для управления метриками и их временными значениями.

## Быстрый старт
### 1. Клонируйте репозиторий

```bash
git clone <repo-url>
cd metrics_project
```

### 2. Настройте переменные окружения

```bash
cp .env.example .env
# При необходимости измените значения в .env
```

Основные переменные:
 # 5 minutes
```env
SECRET_KEY=your-secret-key-change-in-production
POSTGRES_DB=metrics_db
POSTGRES_USER=metrics_user
POSTGRES_PASSWORD=metrics_pass
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

### 3. Запустите через docker-compose

```bash
docker compose up --build
```

При старте автоматически выполняются:
- `migrate` — применяются все миграции
- `create_superuser` — создаётся суперпользователь из `.env` (если не существует)

Проверить, что новые миграции не забыты:

```bash
docker-compose exec web python manage.py makemigrations --check --dry-run
```

Приложение будет доступно по адресу: **http://localhost:8000**

---

## Работа с проектом

### Админ-панель

Откройте **http://localhost:8000/admin/**

## API Эндпоинты

### Авторизация

#### Получить JWT токен
```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

Ответ:
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```
#### Обновить токен
```http
POST /api/token/refresh/
Content-Type: application/json

{ "refresh": "<refresh_token>" }
```

---

### Метрики

#### Создать метрику
```http
POST /api/metrics/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "CPU Usage",
  "description": "Загрузка процессора",
  "unit": "%"
}
```

#### Список метрик пользователя
```http
GET /api/metrics/
Authorization: Bearer <token>
```

---

### Теги

#### Список тегов
```http
GET /api/tags/
Authorization: Bearer <token>
```

---

### Записи метрик

#### Список записей метрики (кэшируется на 5 минут)
```http
GET /api/metrics/{metric_id}/records/
Authorization: Bearer <token>
```

#### Детализация одной записи
```http
GET /api/metrics/{metric_id}/records/{record_id}/
Authorization: Bearer <token>
```

#### Создать запись метрики
```http
POST /api/metrics/{metric_id}/records/
Authorization: Bearer <token>
Content-Type: application/json

{
  "value": "98.6",
  "recorded_at": "2024-04-01T12:00:00Z",
  "tag_ids": [1, 2],
  "note": "Пиковая нагрузка"
}
```
## Celery Beat — Fake Report

Каждые **2 минуты** Celery Beat запускает задачу, которая создаёт/обновляет файл:

```
reports/report.txt
```

---

## Запуск тестов

```bash
# Через Docker
docker compose exec web pytest apps/metrics/tests/ -v

# Только тест на создание записи
docker compose exec web pytest apps/metrics/tests/test_create_record.py -v
```
