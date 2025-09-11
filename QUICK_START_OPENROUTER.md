# 🚀 Быстрый старт: OpenRouter Integration

## Предварительные требования

1. **API ключ OpenRouter** - получите на [openrouter.ai](https://openrouter.ai)
2. **MySQL база данных** - должна быть настроена и доступна
3. **Python 3.8+** - установлен в системе

## Шаг 1: Установка зависимостей

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Шаг 2: Тестирование OpenRouter API

```bash
# Установите ваш API ключ
export OPENROUTER_API_KEY="sk-or-v1-ваш-ключ-здесь"

# Запустите тест
python test_openrouter.py
```

Ожидаемый вывод:
```
🚀 OpenRouter Integration Test
==================================================
🔑 API ключ найден
🧪 Начинаем тестирование интеграции с OpenRouter...

1️⃣ Тестирование подключения...
   ✅ Connection successful

2️⃣ Получение баланса аккаунта...
   💰 Баланс: $25.50
   📊 Использовано: $4.50

3️⃣ Получение доступных моделей...
   📝 Текстовые модели: 15
      • GPT-4 Turbo (OpenAI)
      • Claude 3 Opus (Anthropic)
      • Gemini Pro (Google)
   🖼️  Модели для изображений: 5
   🎵 Модели для аудио: 3

4️⃣ Тестирование простого запроса...
   🤖 Используем модель: openai/gpt-3.5-turbo
   💬 Ответ модели: Привет! У меня всё отлично, спасибо!

✅ Тестирование завершено успешно!
```

## Шаг 3: Запуск backend сервера

```bash
# Убедитесь, что виртуальное окружение активно
source venv/bin/activate

# Запустите сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Шаг 4: Настройка в веб-интерфейсе

1. Откройте фронтенд приложения
2. Перейдите в **Настройки**
3. На вкладке **"API ключи"** добавьте ваш OpenRouter API ключ
4. Перейдите на вкладку **"AI Модели"**
5. Нажмите **"Обновить"** для загрузки доступных моделей
6. Выберите модели для каждого типа:
   - **Текст**: например, `openai/gpt-3.5-turbo`
   - **Анализ изображений (Vision)**: например, `openai/gpt-4-vision-preview`
   - **Генерация изображений**: например, `openai/dall-e-3`
   - **Аудио**: например, `openai/whisper-1`

## Шаг 5: Проверка работы

### Через веб-интерфейс:
- Нажмите **"Баланс"** для просмотра текущего баланса
- Модели сохраняются автоматически при выборе

### Через API:
```bash
# Получить доступные модели
curl -X GET "http://localhost:8000/api/v1/settings/openrouter/models" \
     -H "Content-Type: application/json" \
     --cookie "session=ваша-сессия"

# Получить баланс
curl -X GET "http://localhost:8000/api/v1/settings/openrouter/balance" \
     -H "Content-Type: application/json" \
     --cookie "session=ваша-сессия"

# Тест подключения
curl -X POST "http://localhost:8000/api/v1/settings/openrouter/test-connection" \
     -H "Content-Type: application/json" \
     --cookie "session=ваша-сессия"
```

## Возможные проблемы и решения

### ❌ "API key not configured"
**Решение**: Убедитесь, что API ключ добавлен в настройках и пользователь авторизован

### ❌ "Rate limit exceeded"
**Решение**: Подождите несколько минут, OpenRouter имеет лимиты запросов

### ❌ "Invalid API key"
**Решение**: Проверьте правильность API ключа на [openrouter.ai](https://openrouter.ai)

### ❌ "Network error"
**Решение**: Проверьте подключение к интернету и доступность openrouter.ai

## Структура файлов

```
backend/
├── app/
│   ├── services/
│   │   └── openrouter_service.py    # 🆕 Сервис OpenRouter
│   ├── api/v1/
│   │   └── settings_router.py       # ✏️ Обновлен с новыми эндпоинтами
│   ├── services/
│   │   └── settings_service.py      # ✏️ Добавлены методы OpenRouter
│   └── schemas/
│       └── settings_schema.py       # ✏️ Новые схемы данных
├── test_openrouter.py               # 🆕 Тестовый скрипт
└── OPENROUTER_INTEGRATION.md        # 🆕 Документация
```

```
frontend/
└── src/
    └── components/
        └── Settings.tsx             # ✏️ Новая вкладка "AI Модели"
```

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/settings/openrouter/models` | Получить доступные модели |
| GET | `/api/v1/settings/openrouter/balance` | Получить баланс аккаунта |
| POST | `/api/v1/settings/openrouter/test-connection` | Тест подключения |
| POST | `/api/v1/settings/models` | Сохранить выбранную модель |
| GET | `/api/v1/settings/models` | Получить сохраненные модели |

## Безопасность

✅ **API ключи шифруются** перед сохранением в базу данных  
✅ **Маскированное отображение** ключей в интерфейсе  
✅ **Валидация входных данных** через Pydantic схемы  
✅ **Обработка ошибок** и rate limiting  

## Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Запустите `test_openrouter.py` для диагностики
3. Убедитесь в правильности настройки базы данных
4. Проверьте доступность openrouter.ai

---

🎉 **Готово!** Ваша интеграция с OpenRouter настроена и готова к использованию!
