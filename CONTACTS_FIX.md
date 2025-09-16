# Исправление системы контактов - Устранение дублирования и интеграция с бизнес-аккаунтами

## Проблемы, которые были решены

### 1. Дублирование записей при сохранении в AccountModal.tsx
**Проблема**: При каждом сохранении в `AccountModal.tsx` создавалась новая запись в базе данных, что приводило к дублированию контактов.

**Решение**:
- Интегрировали фронтенд с API контактов вместо локального хранения в localStorage
- Добавили проверку существования контакта по `telegram_user_id` перед созданием
- Если контакт уже существует, выполняется обновление вместо создания нового

### 2. Неправильная привязка к "менеджерам"
**Проблема**: В поле "Ответственный менеджер" отображались менеджеры CRM, а должны были отображаться бизнес-аккаунты, на которые пользователь написал.

**Решение**:
- Заменили поле "Ответственный менеджер" на "Бизнес-аккаунт (на который написал пользователь)"
- Изменили логику выбора с `managers` на `businessAccounts`
- Обновили маппинг данных для корректной связи контакта с бизнес-аккаунтом

## Внесенные изменения

### Frontend изменения

#### 1. AccountModal.tsx
```typescript
// Было:
const { activeManager } = useAppContext();
const { managers } = useAppContext();
manager_id?: number;

// Стало:
const { businessAccounts, activeBusinessAccount } = useAppContext();
business_account_id?: number;
```

- Изменили интерфейс `FormData` с `manager_id` на `business_account_id`
- Обновили селект для выбора бизнес-аккаунта вместо менеджера
- Сделали функции `onCreate` и `onUpdate` асинхронными
- Добавили обработку ошибок при сохранении

#### 2. AppContext.tsx
```typescript
// Новые функции API интеграции:
loadContacts: () => Promise<void>;
addAccount: (account: Omit<Account, 'id'>) => Promise<void>;
updateAccount: (id: number, updates: Partial<Account>) => Promise<void>;
isLoadingContacts: boolean;
```

**Ключевые изменения**:
- Заменили localStorage на API вызовы
- Добавили проверку существования контакта по `telegram_user_id`
- Реализовали автоматическое создание взаимодействий с бизнес-аккаунтами
- Добавили трансформацию данных между API и фронтендом форматами

#### 3. Компоненты (BusinessChatWindow.tsx, ChatWindow.tsx, AccountsManager.tsx)
- Обновили обработчики `onCreate` и `onUpdate` для работы с асинхронными функциями
- Добавили обработку ошибок с пользовательскими уведомлениями
- Предотвращение закрытия модала при ошибках

### Backend (без изменений)
Backend API уже был готов и работал корректно. Изменения потребовались только во фронтенде для правильной интеграции.

## Как это работает теперь

### 1. Предотвращение дублирования
```typescript
// В addAccount функции:
const existingContact = await fetch(`${API_BASE_URL}/api/v1/contacts/telegram/${account.user_id}`);

if (existingContact.ok) {
  // Контакт существует - обновляем
  const existing = await existingContact.json();
  await updateAccount(existing.id, account);
  return;
}

// Контакта нет - создаем новый
```

### 2. Правильная привязка к бизнес-аккаунтам
```typescript
// Создание взаимодействия с бизнес-аккаунтом:
if (account.manager_id) { // manager_id теперь содержит business_account_id
  await fetch(`${API_BASE_URL}/api/v1/contacts/interactions/`, {
    method: 'POST',
    body: JSON.stringify({
      contact_id: newContact.id,
      business_account_id: account.manager_id,
      messages_count: account.total_messages || 0,
      first_interaction: new Date().toISOString(),
      last_interaction: new Date().toISOString()
    }),
  });
}
```

### 3. Автоматическая загрузка данных
```typescript
// В useEffect AppContext:
loadContacts();           // Загружаем контакты из API
loadBusinessAccounts();   // Загружаем бизнес-аккаунты
```

## Результат

✅ **Дублирование устранено**: Каждый контакт создается только один раз, повторные сохранения обновляют существующую запись

✅ **Правильная привязка**: Контакты теперь правильно привязываются к бизнес-аккаунтам, на которые они написали

✅ **Поддержка множественных связей**: Один пользователь может быть связан с несколькими бизнес-аккаунтами

✅ **Синхронизация данных**: Фронтенд синхронизируется с backend через API, данные всегда актуальны

✅ **Обработка ошибок**: Пользователь получает понятные уведомления об ошибках

## Тестирование

Для тестирования:
1. Откройте фронтенд приложения
2. Перейдите к чату в Business Accounts
3. Создайте контакт через AccountModal
4. Убедитесь, что:
   - Контакт создается без дублирования
   - В поле "Бизнес-аккаунт" отображаются правильные бизнес-аккаунты
   - Повторное сохранение обновляет существующую запись
   - Данные корректно сохраняются в базе данных

## API Endpoints используемые

- `GET /api/v1/contacts/` - Загрузка контактов
- `GET /api/v1/contacts/telegram/{telegram_user_id}` - Проверка существования контакта
- `POST /api/v1/contacts/` - Создание нового контакта
- `PUT /api/v1/contacts/{contact_id}` - Обновление контакта
- `POST /api/v1/contacts/interactions/` - Создание взаимодействия с бизнес-аккаунтом
- `GET /api/v1/business-accounts/` - Загрузка бизнес-аккаунтов
