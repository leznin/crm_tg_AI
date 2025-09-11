# OpenRouter Integration Documentation

## Обзор

Интеграция с OpenRouter API позволяет выбирать различные AI модели для работы с текстом, изображениями и аудио. API ключи хранятся в зашифрованном виде в базе данных MySQL.

## Архитектура

### Backend Components

1. **OpenRouterService** (`app/services/openrouter_service.py`)
   - Основной сервис для взаимодействия с OpenRouter API
   - Получение списка доступных моделей
   - Получение баланса аккаунта
   - Тестирование подключения
   - Отправка запросов к моделям

2. **OpenRouterModelManager** (`app/services/openrouter_service.py`)
   - Менеджер для управления моделями с интеграцией базы данных
   - Группировка моделей по типам (text, image, audio)
   - Управление жизненным циклом соединений

3. **Settings Service** (`app/services/settings_service.py`)
   - Расширен методами для работы с OpenRouter
   - `get_available_openrouter_models()` - получение доступных моделей
   - `get_openrouter_balance()` - получение баланса
   - `test_openrouter_connection()` - тест соединения

4. **API Endpoints** (`app/api/v1/settings_router.py`)
   - `GET /api/v1/settings/openrouter/models` - получить доступные модели
   - `GET /api/v1/settings/openrouter/balance` - получить баланс
   - `POST /api/v1/settings/openrouter/test-connection` - тест соединения

### Database Schema

Существующие таблицы используются для хранения:

- **api_keys** - зашифрованные API ключи OpenRouter
- **openrouter_models** - выбранные пользователем модели по типам
- **prompts** - промпты для AI моделей

### Frontend Components

Обновлен компонент `Settings.tsx`:
- Новая вкладка "AI Модели" 
- Выбор моделей для текста, изображений и аудио
- Отображение баланса аккаунта
- Автосохранение выбранных моделей

## Использование

### 1. Настройка API ключа

1. Получите API ключ на [openrouter.ai](https://openrouter.ai)
2. В настройках приложения на вкладке "API ключи" добавьте OpenRouter API Key
3. Ключ автоматически шифруется и сохраняется в базе данных

### 2. Выбор моделей

1. Перейдите на вкладку "AI Модели" в настройках
2. Нажмите "Обновить" для загрузки доступных моделей
3. Выберите модели для каждого типа данных:
   - **Текст** - для анализа сообщений и генерации ответов
   - **Изображения** - для анализа и описания изображений
   - **Аудио** - для транскрипции голосовых сообщений

### 3. Мониторинг баланса

- Нажмите кнопку "Баланс" для просмотра текущего баланса аккаунта
- Отображается потраченная сумма и остаток средств

## Безопасность

- Все API ключи хранятся в зашифрованном виде
- Используется библиотека `cryptography` для шифрования
- Ключи дешифруются только при необходимости выполнения запросов
- В интерфейсе отображаются только маскированные версии ключей

## Обработка ошибок

Система обрабатывает следующие ошибки:
- Неверный или отсутствующий API ключ
- Превышение лимитов запросов (rate limiting)
- Сетевые ошибки
- Ошибки парсинга ответов API

## Модели по умолчанию

При первом использовании рекомендуется выбрать:
- **Текст**: gpt-3.5-turbo или claude-3-haiku (экономичные варианты)
- **Изображения**: gpt-4-vision-preview или claude-3-opus (для анализа изображений)
- **Аудио**: whisper-1 (для транскрипции)

## API Endpoints

### GET /api/v1/settings/openrouter/models
Возвращает доступные модели, сгруппированные по типам.

**Response:**
```json
{
  "text": [
    {
      "id": "openai/gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "description": "Fast and efficient model",
      "context_length": 4096,
      "pricing": {
        "prompt_cost": "$0.50/1M tokens",
        "completion_cost": "$1.50/1M tokens"
      },
      "provider": "OpenAI",
      "capabilities": ["text"]
    }
  ],
  "image": [...],
  "audio": [...]
}
```

### GET /api/v1/settings/openrouter/balance
Возвращает информацию о балансе аккаунта.

**Response:**
```json
{
  "balance": 25.50,
  "usage": 4.50,
  "formatted_balance": "$25.50",
  "formatted_usage": "$4.50",
  "rate_limit": {...}
}
```

### POST /api/v1/settings/openrouter/test-connection
Тестирует подключение к OpenRouter API.

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "status": "success"
}
```

## Требования

- Python 3.8+
- httpx для HTTP запросов
- Действующий API ключ OpenRouter
- MySQL база данных для хранения настроек
