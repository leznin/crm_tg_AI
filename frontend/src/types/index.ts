export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  is_bot: boolean;
}

export interface Chat {
  id: number;
  type: 'private' | 'group' | 'supergroup' | 'channel';
  title?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  photo?: string;
  last_message?: Message;
  unread_count: number;
  pinned: boolean;
  muted: boolean;
  is_bot_chat: boolean; // Indicates if this is a bot chat
  // Владение: менеджер (сотрудник), под которым отображается чат
  manager_id: number;
}

export interface Manager {
  id: number;
  name: string;
  telegram_user_id?: number; // опционально для связи
  role?: 'manager' | 'admin';
  created_at: string;
}

export interface Message {
  id: number;
  chat_id: number;
  sender_id: number;
  text: string;
  date: number;
  reply_to_message?: Message;
  from_me: boolean;
}

export interface Account {
  id: number;
  user_id: number;
  username?: string;
  // История username: последний (актуальный) хранится в поле username, предыдущее остаётся в history
  username_history?: { username: string; changed_at: string }[];
  first_name: string;
  last_name?: string;
  rating: number; // 1-5 stars
  tags: string[];
  category: 'client' | 'partner' | 'lead' | 'spam' | 'other';
  notes: string;
  source: 'private' | 'group'; // Whether from private message or group chat
  created_at: string;
  last_contact: string;
  total_messages: number;
  chat_type?: 'private' | 'group' | 'supergroup' | 'channel';
  // Дополнительные бизнес-поля (2025 UI)
  registration_date?: string; // Дата регистрации аккаунта (внешняя)
  brand_name?: string;        // Имя бренда / компания
  position?: string;          // Должность контакта
  years_in_market?: number;   // Сколько лет на рынке
  // Владелец (менеджер). Может быть переназначен.
  manager_id?: number;
}

export interface ChatSummary {
  chat_id: number;
  summary: string;
  key_points: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
  last_updated: string;
}

export interface ApiConfig {
  telegram_bot_token?: string;
  openrouter_api_key?: string;
}

export interface AnalyticsData {
  daily_chats: number;
  new_contacts: number;
  total_messages: number;
  average_rating: number;
  top_categories: { category: string; count: number }[];
  activity_chart: { date: string; messages: number; chats: number }[];
}

// Участник чата (локально храним только user_id; подробности берём из Account при наличии)
export interface ChatMember {
  chat_id: number;
  user_id: number;
  added_at: string; // ISO timestamp
  // Снимок данных пользователя (на момент добавления / последнего обновления)
  user?: TelegramUser;
  role?: 'member' | 'admin' | 'creator' | 'restricted' | 'left' | 'kicked';
}

// Запись передачи лида поставщику (или наоборот) внутри системы.
// Используются только Telegram-данные через ссылки на существующие Account (никаких e-mail и т.п.).
export interface TransferRecord {
  id: number;
  supplier_account_id: number; // ID аккаунта поставщика
  client_account_id: number;   // ID аккаунта лида / клиента
  created_at: string;          // Дата создания связи
  status: 'new' | 'in_progress' | 'completed' | 'cancelled';
  notes?: string;              // Короткие заметки (опционально)
}

// Business Accounts для интеграции с Telegram Business
export interface BusinessAccount {
  id: number;
  business_connection_id: string;
  user_id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  is_enabled: boolean;
  can_reply: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessChat {
  id: number;
  chat_id: number;
  business_account_id: number;
  chat_type: 'private' | 'group' | 'supergroup' | 'channel';
  title?: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  unread_count: number;
  message_count: number;
  created_at: string;
  updated_at: string;
  last_message_at?: string;
  last_message?: BusinessMessage;
}

export interface BusinessMessage {
  id: number;
  message_id: number;
  chat_id: number;
  sender_id: number;
  sender_first_name?: string;
  sender_last_name?: string;
  sender_username?: string;
  text?: string;
  message_type: 'text' | 'photo' | 'document' | 'voice' | 'video';
  file_id?: string;
  file_unique_id?: string;
  file_name?: string;
  file_size?: number;
  mime_type?: string;
  is_outgoing: boolean;
  created_at: string;
  telegram_date: string;
}

export interface BusinessAccountStats {
  chats_count: number;
  messages_count: number;
  unread_chats_count: number;
  account_name: string;
  username?: string;
  is_enabled: boolean;
}