# Система управления контактами для Telegram Business CRM

## Обзор

Реализована полная система записи и управления контактами пользователей, которые пишут в бизнес-аккаунты. Система автоматически создает записи контактов при получении сообщений через Telegram Business API и предоставляет богатый функционал для работы с ними.

## Основные компоненты

### 1. Модели данных (`app/models/contact.py`)

#### Contact (Контакт)
- **telegram_user_id**: ID пользователя в Telegram
- **first_name, last_name, username**: Базовая информация о пользователе
- **username_history**: История изменений username (JSON)
- **rating**: Рейтинг от 1 до 5 звезд
- **category**: Категория (lead, client, partner, spam, other)
- **source**: Источник (private, group)
- **tags**: Теги (JSON массив)
- **notes**: Заметки
- **registration_date**: Дата регистрации аккаунта пользователя
- **brand_name**: Название бренда/компании
- **position**: Должность
- **years_in_market**: Количество лет на рынке
- **total_messages**: Общее количество сообщений
- **last_contact**: Дата последнего контакта

#### ContactBusinessInteraction (Взаимодействие с бизнес-аккаунтом)
- **contact_id**: Ссылка на контакт
- **business_account_id**: Ссылка на бизнес-аккаунт
- **messages_count**: Количество сообщений для этого бизнес-аккаунта
- **first_interaction**: Дата первого взаимодействия
- **last_interaction**: Дата последнего взаимодействия
- **notes**: Заметки специфичные для этого бизнес-аккаунта
- **status**: Статус (active, blocked, archived)

### 2. API Эндпоинты (`app/api/v1/contact_router.py`)

#### Основные операции
- `GET /api/v1/contacts/` - Получить список контактов с фильтрацией и пагинацией
- `GET /api/v1/contacts/{contact_id}` - Получить контакт по ID
- `GET /api/v1/contacts/telegram/{telegram_user_id}` - Получить контакт по Telegram ID
- `POST /api/v1/contacts/` - Создать новый контакт
- `PUT /api/v1/contacts/{contact_id}` - Обновить контакт
- `DELETE /api/v1/contacts/{contact_id}` - Удалить контакт

#### Статистика и аналитика
- `GET /api/v1/contacts/stats` - Получить общую статистику по контактам
- `GET /api/v1/contacts/recent` - Получить недавно добавленные контакты
- `GET /api/v1/contacts/top-by-messages` - Топ контактов по количеству сообщений

#### Фильтрация по бизнес-аккаунтам
- `GET /api/v1/contacts/business-account/{business_account_id}` - Контакты конкретного бизнес-аккаунта

#### Управление тегами
- `POST /api/v1/contacts/{contact_id}/tags/{tag}` - Добавить тег
- `DELETE /api/v1/contacts/{contact_id}/tags/{tag}` - Удалить тег

#### Управление рейтингом
- `PUT /api/v1/contacts/{contact_id}/rating/{rating}` - Обновить рейтинг

#### Блокировка/разблокировка
- `POST /api/v1/contacts/{contact_id}/block/{business_account_id}` - Заблокировать для бизнес-аккаунта
- `POST /api/v1/contacts/{contact_id}/unblock/{business_account_id}` - Разблокировать

### 3. Автоматическая обработка webhook'ов

Система интегрирована с Telegram webhook обработчиком (`app/api/v1/telegram_webhook_router.py`):

- При получении сообщения автоматически создается или обновляется контакт
- Учитываются все данные отправителя (имя, фамилия, username)
- Создается запись взаимодействия с конкретным бизнес-аккаунтом
- Ведется статистика сообщений
- Отслеживается история изменений username

## Ключевые особенности

### 1. Связь многие-ко-многим
Один пользователь может писать в несколько бизнес-аккаунтов. Для каждого такого взаимодействия создается отдельная запись с индивидуальной статистикой.

### 2. Автоматическое обновление
При каждом новом сообщении:
- Обновляется информация о контакте (если изменились имя/username)
- Увеличивается счетчик сообщений
- Обновляется время последнего контакта
- Ведется история изменений username

### 3. Богатая фильтрация
API поддерживает фильтрацию по:
- Текстовому поиску (имя, фамилия, username, бренд, должность, заметки)
- Бизнес-аккаунту
- Категории
- Рейтингу
- Тегам

### 4. Статистика и аналитика
- Общее количество контактов
- Новые контакты за день/неделю
- Распределение по категориям и рейтингу
- Топ бизнес-аккаунтов по количеству контактов

## Структура базы данных

```sql
-- Таблица контактов
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    username VARCHAR(255),
    username_history JSON,
    rating INTEGER DEFAULT 1,
    category VARCHAR(50) DEFAULT 'lead',
    source VARCHAR(50) DEFAULT 'private',
    tags JSON,
    notes TEXT,
    registration_date DATETIME,
    brand_name VARCHAR(255),
    position VARCHAR(255),
    years_in_market INTEGER,
    total_messages INTEGER DEFAULT 0,
    last_contact DATETIME,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
    INDEX idx_telegram_user_id (telegram_user_id)
);

-- Таблица взаимодействий с бизнес-аккаунтами
CREATE TABLE contact_business_interactions (
    id INTEGER PRIMARY KEY,
    contact_id INTEGER NOT NULL,
    business_account_id INTEGER NOT NULL,
    messages_count INTEGER DEFAULT 0,
    first_interaction DATETIME NOT NULL,
    last_interaction DATETIME NOT NULL,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (business_account_id) REFERENCES business_accounts(id)
);
```

## Примеры использования

### Получить статистику контактов
```bash
curl -X GET "http://localhost:8000/api/v1/contacts/stats"
```

### Получить контакты с фильтрацией
```bash
curl -X GET "http://localhost:8000/api/v1/contacts/?query=test&category=lead&rating=5&page=1&per_page=10"
```

### Получить контакты конкретного бизнес-аккаунта
```bash
curl -X GET "http://localhost:8000/api/v1/contacts/business-account/1"
```

### Обновить рейтинг контакта
```bash
curl -X PUT "http://localhost:8000/api/v1/contacts/1/rating/5"
```

### Добавить тег контакту
```bash
curl -X POST "http://localhost:8000/api/v1/contacts/1/tags/vip"
```

## Интеграция с фронтендом

Система полностью готова для интеграции с существующим фронтендом. Все данные из `AccountModal.tsx` поддерживаются:

- Имя, фамилия, username
- Рейтинг (звезды)
- Категория и источник
- Теги и заметки
- Дата регистрации
- Бизнес-информация (бренд, должность, годы на рынке)
- **Вместо "менеджера" используется связь с бизнес-аккаунтом**

Один контакт может быть связан с несколькими бизнес-аккаунтами, что позволяет отслеживать все взаимодействия пользователя с различными бизнесами в системе.
