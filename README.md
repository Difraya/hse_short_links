# Short Links API

API-сервис для создания коротких ссылок с возможностью кастомизации, отслеживания статистики и автоматического удаления по сроку действия.

---

## Возможности

- Генерация коротких ссылок (с кастомным алиасом или случайным кодом)
- Редирект на оригинальный URL
- Просмотр статистики использования ссылки
- Удаление и обновление ссылок
- Аутентификация и авторизация пользователей (JWT)
- Автоматическое удаление просроченных ссылок (Celery + Redis)
- Кэширование популярных ссылок (Redis)

## Примеры запросов

### Регистрация
**POST** `/auth/register`
```json
{
  "email": "user@example.com",
  "password": "strongpassword",
  "username": "your_username"
}
```
Ответ:
```json
{
  "id": "fb1c0618-...",
  "email": "user@example.com",
  "username": "your_username"
}
```

### Сокращение ссылки
**POST** `/links/shorten`
```json
{
  "original_url": "https://example.com/page",
  "custom_alias": "my-alias",        // необязательно
  "expires_at": "2025-04-10T12:00"    // необязательно
}
```
Ответ:
```json
{
  "short_url": "http://localhost:8000/my-alias"
}
```

### Переход по короткой ссылке
**GET** `/{short_code}`
- Перенаправляет на оригинальный URL

### Получение статистики
**GET** `/links/{short_code}/stats`

Ответ:
```json
{
  "original_url": "https://example.com/",
  "create_at": "2025-03-31T21:59:40.725Z",
  "click_count": 0,
  "last_use": "2025-03-31T21:59:40.725Z"
}
```

### Удаление ссылки
**DELETE** `/links/{short_code}`

### Обновление ссылки
**PUT** `/links/{short_code}`
```json
{
  "original_url": "https://new-url.com",
  "custom_alias": "new-alias"
}
```

### Поиск по оригинальному URL
**GET** `/links/search?original_url=https://example.com`

Ответ:
```json
{
  "short_url": "string",
  "original_url": "https://example.com/",
  "create_at": "2025-03-31T22:01:24.084Z"
}
```
---

## Инструкция по запуску

1. Склонировать репозиторий:
```bash
git clone https://github.com/yourusername/hse_short_links.git
cd hse_short_links
```

2. Заполнить файл `.env`

3. Запустить проект:
```bash
docker-compose up --build
```

4. Открыть в браузере: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Структура БД 
Таблица `user`

| Поле            | Тип      | Описание                |
|-----------------|----------|-------------------------|
| id              | UUID     | Уникальный идентификатор |
| username        | String   | Имя пользователя        |
| email           | String   | Электронная почта       |
| hashed_password | String   | Хешированный пароль     |
| registered_at   | datetime (UTC) | Дата регистрации        |


Таблица `link`

| Поле         | Тип     | Описание                     |
|--------------|---------|------------------------------|
| id           | UUID    | Уникальный идентификатор    |
| original_url | String  | Оригинальный URL            |
| short_url    | String  | Короткий код                |
| custom_alias | String (null) | Кастомный алиас             |
| create_at    | datetime (UTC) | Дата создания               |
| expires_at   | datetime (UTC) | Дата истечения              |
| last_use     | datetime (UTC) | Последнее использование     |
| click_count  | Integer | Количество переходов        |
| user_id      | UUID    | Владелец ссылки             |

---

## Очистка просроченных ссылок
- Запускается каждый час с помощью **Celery Beat**
- Удаляет ссылки, у которых `expires_at < текущей даты`

---

## Кэширование
- Популярные ссылки хранятся в Redis
- При обновлении или удалении кэш очищается


