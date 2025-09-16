import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { Chat, Account, ChatSummary, ApiConfig, AnalyticsData, Message, TransferRecord, Manager, ChatMember, BusinessAccount, BusinessChat, BusinessMessage } from '../types';

const API_BASE_URL = 'http://localhost:8000';

interface AppContextType {
  // API Configuration
  apiConfig: ApiConfig;
  updateApiConfig: (config: Partial<ApiConfig>) => Promise<void>;

  // Managers (workspace owners)
  managers: Manager[];
  activeManager: Manager | null;
  setActiveManager: (m: Manager | null) => void;
  addManager: (name: string, telegram_user_id?: number) => Manager;
  updateManager: (id: number, updates: Partial<Omit<Manager,'id'>>) => void;
  deleteManager: (id: number) => void;

  // Chats
  chats: Chat[];
  activeChat: Chat | null;
  setActiveChat: (chat: Chat | null) => void;
  getChatsForManager: (managerId: number) => Chat[];
  addChat: (managerId: number, chat: Omit<Chat, 'id' | 'manager_id'>) => Chat;
  
  // Messages
  messages: Message[];
  sendMessage: (chatId: number, text: string) => void;
  
  // Accounts
  accounts: Account[];
  addAccount: (account: Omit<Account, 'id'>) => void;
  createAccountFromChat: (chat: Chat, senderId: number) => void;
  updateAccount: (id: number, updates: Partial<Account>) => void;
  deleteAccount: (id: number) => void;
  getAccountByUserId: (userId: number) => Account | undefined;
  
  // Chat summaries
  chatSummaries: ChatSummary[];
  getChatSummary: (chatId: number) => ChatSummary | undefined;
  
  // Analytics
  analyticsData: AnalyticsData;

  // Transfer Records (CRM передачи)
  transferRecords: TransferRecord[];
  addTransferRecord: (data: Omit<TransferRecord, 'id' | 'created_at'>) => void;
  updateTransferRecord: (id: number, updates: Partial<TransferRecord>) => void;
  deleteTransferRecord: (id: number) => void;
  getTransfersByAccount: (accountId: number) => TransferRecord[];
  
  // UI State
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  sidebarOpen: boolean; // отображение off-canvas на мобильных
  setSidebarOpen: (open: boolean) => void;
  currentView: 'chats' | 'accounts' | 'analytics' | 'settings' | 'transfers' | 'botchats';
  setCurrentView: (view: 'chats' | 'accounts' | 'analytics' | 'settings' | 'transfers' | 'botchats') => void;

  // Chat members (участники групп, где бот администратор)
  chatMembers: ChatMember[];
  getMembersForChat: (chatId: number) => ChatMember[];
  addMembersBulk: (chatId: number, userIds: number[]) => void;
  // Keywords (настройка для поиска сообщений)
  keywords: string[];
  setKeywords: (kw: string[]) => void;

  // OpenRouter Balance
  balance: {
    balance: number;
    usage: number;
    formatted_balance: string;
    formatted_usage: string;
  } | null;
  isLoadingBalance: boolean;
  loadBalance: () => Promise<void>;

  // Business Accounts
  businessAccounts: BusinessAccount[];
  activeBusinessAccount: BusinessAccount | null;
  setActiveBusinessAccount: (account: BusinessAccount | null) => void;
  loadBusinessAccounts: () => Promise<void>;
  isLoadingBusinessAccounts: boolean;

  // Business Chats
  businessChats: BusinessChat[];
  activeBusinessChat: BusinessChat | null;
  setActiveBusinessChat: (chat: BusinessChat | null) => void;
  loadBusinessChats: (accountId: number) => Promise<void>;
  isLoadingBusinessChats: boolean;

  // Business Messages
  businessMessages: BusinessMessage[];
  loadBusinessMessages: (chatId: number, limit?: number, offset?: number) => Promise<void>;
  sendBusinessMessage: (connectionId: string, chatId: number, text: string) => Promise<void>;
  sendBusinessPhoto: (connectionId: string, chatId: number, fileId: string, caption?: string) => Promise<void>;
  sendBusinessDocument: (connectionId: string, chatId: number, fileId: string, caption?: string) => Promise<void>;
  uploadFile: (file: File) => Promise<{file_id: string; message_type: string}>;
  isLoadingBusinessMessages: boolean;
  isSendingMessage: boolean;
}

const AppContext = createContext<AppContextType | null>(null);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiConfig, setApiConfig] = useState<ApiConfig>({});
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [managers, setManagers] = useState<Manager[]>([]);
  const [activeManager, setActiveManager] = useState<Manager | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [chatSummaries, setChatSummaries] = useState<ChatSummary[]>([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true); // off-canvas visibility (mobile)
  const [currentView, setCurrentView] = useState<'chats' | 'accounts' | 'analytics' | 'settings' | 'transfers' | 'botchats'>('chats');
  const [transferRecords, setTransferRecords] = useState<TransferRecord[]>([]);
  const [chatMembers, setChatMembers] = useState<ChatMember[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);

  // OpenRouter Balance state
  const [balance, setBalance] = useState<{
    balance: number;
    usage: number;
    formatted_balance: string;
    formatted_usage: string;
  } | null>(null);
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);

  // Business Accounts state
  const [businessAccounts, setBusinessAccounts] = useState<BusinessAccount[]>([]);
  const [activeBusinessAccount, setActiveBusinessAccount] = useState<BusinessAccount | null>(null);
  const [isLoadingBusinessAccounts, setIsLoadingBusinessAccounts] = useState(false);

  // Business Chats state
  const [businessChats, setBusinessChats] = useState<BusinessChat[]>([]);
  const [activeBusinessChat, setActiveBusinessChat] = useState<BusinessChat | null>(null);
  const [isLoadingBusinessChats, setIsLoadingBusinessChats] = useState(false);

  // Business Messages state
  const [businessMessages, setBusinessMessages] = useState<BusinessMessage[]>([]);
  const [isLoadingBusinessMessages, setIsLoadingBusinessMessages] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // --- Migration & Initial Load ---
  useEffect(() => {
    // Only load data if user is authenticated
    // This is an additional safety check since AppProvider should only be mounted for authenticated users
    const isLoggedIn = localStorage.getItem('telegram_crm_logged_in');
    if (!isLoggedIn) {
      console.warn('AppProvider loaded without authentication - this should not happen');
      return;
    }
    
    // Load API config from server instead of localStorage
    loadApiConfigFromServer();
    
    // Keep localStorage as fallback for migration
    const savedConfig = localStorage.getItem('telegram_crm_config');
    if (savedConfig) {
      try {
        const config = JSON.parse(savedConfig);
        // Migrate to server only if data exists and is not empty
        const hasValidToken = config.telegram_bot_token && config.telegram_bot_token.trim().length > 0;
        const hasValidApiKey = config.openrouter_api_key && config.openrouter_api_key.trim().length > 0;
        
        if (hasValidToken || hasValidApiKey) {
          migrateConfigToServer(config);
        } else {
          // Remove empty config from localStorage to prevent future migration attempts
          localStorage.removeItem('telegram_crm_config');
        }
      } catch (error) {
        console.error('Error parsing localStorage config:', error);
        localStorage.removeItem('telegram_crm_config');
      }
    }

    const savedAccountsRaw = localStorage.getItem('telegram_crm_accounts');
    if (savedAccountsRaw) {
      try { setAccounts(JSON.parse(savedAccountsRaw)); } catch {}
    }

    const savedTransfers = localStorage.getItem('telegram_crm_transfers');
    if (savedTransfers) setTransferRecords(JSON.parse(savedTransfers));

    const savedKeywords = localStorage.getItem('telegram_crm_keywords');
    if (savedKeywords) {
      try { const arr = JSON.parse(savedKeywords); if (Array.isArray(arr)) setKeywords(arr.filter(k => typeof k === 'string')); } catch {}
    }

    const savedManagers = localStorage.getItem('telegram_crm_managers');
    if (savedManagers) { try { setManagers(JSON.parse(savedManagers)); } catch {} }

    const schemaVersion = Number(localStorage.getItem('telegram_crm_schema_version') || '1');
    if (schemaVersion < 3) {
      migrateToManagers();
    } else {
      const storedChats = localStorage.getItem('telegram_crm_chats_v2');
      if (storedChats) { try { setChats(JSON.parse(storedChats)); } catch {} }
      if (!storedChats) loadMockData();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Set initial active manager
  useEffect(() => {
    if (!activeManager && managers.length) setActiveManager(managers[0]);
  }, [managers, activeManager]);

  // Assign manager_id to legacy accounts lacking it
  useEffect(() => {
    if (!managers.length || !accounts.length) return;
    const primaryId = managers[0].id;
    const needs = accounts.some(a => a.manager_id == null);
    if (!needs) return;
    setAccounts(prev => {
      const updated = prev.map(a => a.manager_id == null ? { ...a, manager_id: activeManager?.id || primaryId } : a);
      localStorage.setItem('telegram_crm_accounts', JSON.stringify(updated));
      return updated;
    });
  }, [managers, accounts, activeManager]);

  const migrateToManagers = () => {
    // prevVersion <3: chats may have account_id. We'll convert to manager_id.
    let existingChats: any[] = [];
    const raw = localStorage.getItem('telegram_crm_chats_v2');
    if (raw) { try { existingChats = JSON.parse(raw); } catch {} }
    let mgrs: Manager[] = [];
    const rawManagers = localStorage.getItem('telegram_crm_managers');
    if (rawManagers) { try { mgrs = JSON.parse(rawManagers); } catch {} }
    if (mgrs.length === 0) {
      const m: Manager = { id: Date.now(), name: 'Менеджер 1', created_at: new Date().toISOString(), role: 'manager' };
      mgrs = [m];
      localStorage.setItem('telegram_crm_managers', JSON.stringify(mgrs));
      setManagers(mgrs);
    } else {
      setManagers(mgrs);
    }
    const mid = mgrs[0].id;
    const migrated: Chat[] = existingChats.map(c => ({ ...c, manager_id: c.manager_id ?? c.account_id ?? mid }));
    if (migrated.length === 0) {
      const mocks = createMockChats(mid);
      setChats(mocks);
      localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(mocks));
    } else {
      setChats(migrated);
      localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(migrated));
    }
    localStorage.setItem('telegram_crm_schema_version', '3');
  };

  // Transfer Records CRUD (вынесено из useEffect)
  const addTransferRecord = useCallback((data: Omit<TransferRecord, 'id' | 'created_at'>) => {
    setTransferRecords(prev => {
      const newRecord: TransferRecord = {
        ...data,
        id: Date.now(),
        created_at: new Date().toISOString()
      };
      const updated = [newRecord, ...prev];
      localStorage.setItem('telegram_crm_transfers', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const updateTransferRecord = useCallback((id: number, updates: Partial<TransferRecord>) => {
    setTransferRecords(prev => {
      const updated = prev.map(r => r.id === id ? { ...r, ...updates } : r);
      localStorage.setItem('telegram_crm_transfers', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const deleteTransferRecord = useCallback((id: number) => {
    setTransferRecords(prev => {
      const updated = prev.filter(r => r.id !== id);
      localStorage.setItem('telegram_crm_transfers', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const getTransfersByAccount = useCallback((accountId: number) => {
    return transferRecords.filter(r => r.client_account_id === accountId || r.supplier_account_id === accountId);
  }, [transferRecords]);

  const createMockChats = (managerId: number): Chat[] => ([
    {
      id: 1,
      type: 'private',
      first_name: 'John',
      last_name: 'Smith',
      username: 'johnsmith',
      unread_count: 3,
      pinned: true,
      muted: false,
      is_bot_chat: true,
      manager_id: managerId,
      last_message: {
        id: 1,
        chat_id: 1,
        sender_id: 1,
        text: 'Привет! Как дела с проектом?',
        date: Date.now() - 3600000,
        from_me: false
      }
    },
    {
      id: 2,
      type: 'private',
      first_name: 'Anna',
      last_name: 'Johnson',
      username: 'anna_j',
      unread_count: 0,
      pinned: false,
      muted: false,
      is_bot_chat: true,
  manager_id: managerId,
      last_message: {
        id: 2,
        chat_id: 2,
        sender_id: 2,
        text: 'Спасибо за предложение!',
        date: Date.now() - 7200000,
        from_me: true
      }
    },
    {
      id: 3,
      type: 'group',
      title: 'Team Discussion',
      unread_count: 12,
      pinned: false,
      muted: true,
      is_bot_chat: true,
  manager_id: managerId,
      last_message: {
        id: 3,
        chat_id: 3,
        sender_id: 3,
        text: 'Встреча завтра в 10:00',
        date: Date.now() - 1800000,
        from_me: false
      }
    }
  ]);

  const loadMockData = () => {
    setManagers(prev => {
      let list = prev;
      if (list.length === 0) {
        const m: Manager = { id: Date.now(), name: 'Менеджер 1', created_at: new Date().toISOString(), role: 'manager' };
        list = [m];
        localStorage.setItem('telegram_crm_managers', JSON.stringify(list));
      }
      const mockChats = createMockChats(list[0].id);
      setChats(mockChats);
      localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(mockChats));
      setChatSummaries([
        {
          chat_id: 1,
          summary: 'Обсуждение текущего проекта и планов на следующую неделю. Клиент заинтересован в дополнительных функциях.',
          key_points: ['Проект почти завершен', 'Нужны дополнительные функции', 'Встреча на следующей неделе'],
          sentiment: 'positive',
          last_updated: new Date().toISOString()
        },
        {
          chat_id: 2,
          summary: 'Переговоры о сотрудничестве. Обсуждение условий и сроков.',
          key_points: ['Условия сотрудничества', 'Сроки реализации', 'Бюджет проекта'],
          sentiment: 'neutral',
          last_updated: new Date().toISOString()
        }
      ]);
      return list;
    });
  };

  // API functions for server communication
  const loadApiConfigFromServer = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/settings/api-config`, {
        credentials: 'include'
      });
      if (response.ok) {
        const config = await response.json();
        setApiConfig(config);
      } else if (response.status === 401) {
        // User not authenticated, use localStorage fallback
        const savedConfig = localStorage.getItem('telegram_crm_config');
        if (savedConfig) {
          setApiConfig(JSON.parse(savedConfig));
        }
      }
    } catch (error) {
      console.error('Failed to load API config from server:', error);
      // Fallback to localStorage
      const savedConfig = localStorage.getItem('telegram_crm_config');
      if (savedConfig) {
        setApiConfig(JSON.parse(savedConfig));
      }
    }
  }, []);

  const migrateConfigToServer = useCallback(async (config: ApiConfig) => {
    try {
      // First check if server already has configuration
      const checkResponse = await fetch(`${API_BASE_URL}/api/v1/settings/api-config`, {
        credentials: 'include'
      });
      
      if (checkResponse.ok) {
        const serverConfig = await checkResponse.json();
        // Only migrate if server config is empty or incomplete
        const serverHasToken = serverConfig.telegram_bot_token && serverConfig.telegram_bot_token.trim().length > 0;
        const serverHasApiKey = serverConfig.openrouter_api_key && serverConfig.openrouter_api_key.trim().length > 0;
        
        if (serverHasToken && serverHasApiKey) {
          // Server already has complete config, just clear localStorage
          localStorage.removeItem('telegram_crm_config');
          return;
        }
        
        // Merge with server config, keeping server values if they exist
        const mergedConfig = {
          telegram_bot_token: serverHasToken ? serverConfig.telegram_bot_token : config.telegram_bot_token,
          openrouter_api_key: serverHasApiKey ? serverConfig.openrouter_api_key : config.openrouter_api_key
        };
        
        await fetch(`${API_BASE_URL}/api/v1/settings/api-config`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(mergedConfig)
        });
      } else {
        // Server doesn't have config, migrate from localStorage
        await fetch(`${API_BASE_URL}/api/v1/settings/api-config`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(config)
        });
      }
      
      // Clear localStorage after successful migration
      localStorage.removeItem('telegram_crm_config');
    } catch (error) {
      console.error('Failed to migrate config to server:', error);
    }
  }, []);

  const updateApiConfig = useCallback(async (config: Partial<ApiConfig>) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/settings/api-config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        const updatedConfig = await response.json();
        setApiConfig(prev => ({ ...prev, ...updatedConfig }));
      } else if (response.status === 401) {
        // User not authenticated, use localStorage
        setApiConfig(prev => {
          const newConfig = { ...prev, ...config };
          localStorage.setItem('telegram_crm_config', JSON.stringify(newConfig));
          return newConfig;
        });
      } else {
        throw new Error(`Server responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to update API config:', error);
      // Fallback to localStorage for offline functionality
      setApiConfig(prev => {
        const newConfig = { ...prev, ...config };
        localStorage.setItem('telegram_crm_config', JSON.stringify(newConfig));
        return newConfig;
      });
    }
  }, []);

  const sendMessage = useCallback((chatId: number, text: string) => {
    const newMessage: Message = {
      id: Date.now(),
      chat_id: chatId,
      sender_id: 0,
      text,
      date: Date.now(),
      from_me: true
    };
    setMessages(prev => [...prev, newMessage]);
    setChats(prev => prev.map(chat => chat.id === chatId ? { ...chat, last_message: newMessage } : chat));
    // Persist chats (only last_message is updated)
    setTimeout(() => {
      localStorage.setItem('telegram_crm_chats_v2', JSON.stringify((prevChatsRef.current)));
    }, 0);
  }, []);

  // Keep a ref to latest chats for persistence after state batching
  const prevChatsRef = React.useRef<Chat[]>([]);
  useEffect(() => { prevChatsRef.current = chats; }, [chats]);

  const getChatsForManager = useCallback((managerId: number) => chats.filter(c => c.manager_id === managerId), [chats]);

  const addChat = useCallback((managerId: number, chat: Omit<Chat, 'id' | 'manager_id'>) => {
    const newChat: Chat = { ...chat, id: Date.now(), manager_id: managerId };
    setChats(prev => {
      const list = [...prev, newChat];
      localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(list));
      return list;
    });
    return newChat;
  }, []);

  const createAccountFromChat = useCallback((chat: Chat, senderId: number) => {
    setAccounts(prev => {
      const existing = prev.find(acc => acc.user_id === senderId);
      if (existing) {
        const updated = prev.map(acc => acc.id === existing.id ? {
          ...acc,
          last_contact: new Date().toISOString(),
          total_messages: acc.total_messages + 1
        } : acc);
        localStorage.setItem('telegram_crm_accounts', JSON.stringify(updated));
        return updated;
      }
      const newAccount: Account = {
        user_id: senderId,
  // Fallback precedence: explicit first name > title > username > placeholder
  first_name: chat.first_name || chat.title || chat.username || 'Без имени',
  last_name: chat.last_name || undefined,
  username: chat.username || undefined,
        // Default rating changed from 3 to 1 (требование: по умолчанию одна звезда)
        rating: 1,
        tags: [],
        category: chat.type === 'private' ? 'lead' : 'other',
        notes: `Автоматически создан из ${chat.type === 'private' ? 'личного чата' : 'группового чата'}`,
        source: chat.type === 'private' ? 'private' : 'group',
        created_at: new Date().toISOString(),
        last_contact: new Date().toISOString(),
        total_messages: 1,
        chat_type: chat.type,
    id: Date.now(),
    manager_id: activeManager?.id || managers[0]?.id
      };
      const newAccounts = [...prev, newAccount];
      localStorage.setItem('telegram_crm_accounts', JSON.stringify(newAccounts));
      return newAccounts;
    });
  }, [activeManager, managers]);

  const getAccountByUserId = useCallback((userId: number) => {
    return accounts.find(account => account.user_id === userId);
  }, [accounts]);

  const addAccount = useCallback((account: Omit<Account, 'id'>) => {
    setAccounts(prev => {
    const newAccount: Account = { ...account, id: Date.now(), manager_id: account.manager_id ?? activeManager?.id ?? managers[0]?.id };
      const newAccounts = [...prev, newAccount];
      localStorage.setItem('telegram_crm_accounts', JSON.stringify(newAccounts));
      return newAccounts;
    });
  }, [activeManager, managers]);

  const updateAccount = useCallback((id: number, updates: Partial<Account>) => {
    setAccounts(prev => {
      const newAccounts = prev.map(account => {
        if (account.id !== id) return account;
        // Track username changes
        let username_history = account.username_history || [];
        if (updates.username && updates.username !== account.username) {
          username_history = [
            { username: account.username || '(empty)', changed_at: new Date().toISOString() },
            ...username_history
          ].slice(0, 20); // keep last 20
        }
  return { ...account, ...updates, username_history };
      });
      localStorage.setItem('telegram_crm_accounts', JSON.stringify(newAccounts));
      return newAccounts;
    });
  }, []);

  const deleteAccount = useCallback((id: number) => {
    setAccounts(prev => {
      const newAccounts = prev.filter(account => account.id !== id);
      localStorage.setItem('telegram_crm_accounts', JSON.stringify(newAccounts));
      return newAccounts;
    });
  }, []); // deleting account no longer affects chats

  // Manager CRUD
  const addManager = useCallback((name: string, telegram_user_id?: number) => {
    const m: Manager = { id: Date.now(), name, telegram_user_id, created_at: new Date().toISOString(), role: 'manager' };
    setManagers(prev => { const list = [...prev, m]; localStorage.setItem('telegram_crm_managers', JSON.stringify(list)); return list; });
    return m;
  }, []);

  const updateManager = useCallback((id: number, updates: Partial<Omit<Manager,'id'>>) => {
    setManagers(prev => { const list = prev.map(mm => mm.id === id ? { ...mm, ...updates } : mm); localStorage.setItem('telegram_crm_managers', JSON.stringify(list)); return list; });
  }, []);

  const deleteManager = useCallback((id: number) => {
    setManagers(prev => { const list = prev.filter(m => m.id !== id); localStorage.setItem('telegram_crm_managers', JSON.stringify(list)); return list; });
    setChats(prev => { const list = prev.filter(c => c.manager_id !== id); localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(list)); return list; });
    if (activeManager?.id === id) { setActiveManager(null); setActiveChat(null); }
  }, [activeManager]);

  const getChatSummary = useCallback((chatId: number) => {
    return chatSummaries.find(summary => summary.chat_id === chatId);
  }, [chatSummaries]);

  // Mock analytics data
  const analyticsData: AnalyticsData = {
    daily_chats: 12,
    new_contacts: 3,
    total_messages: 247,
    average_rating: 4.2,
    top_categories: [
      { category: 'client', count: 45 },
      { category: 'lead', count: 23 },
      { category: 'partner', count: 12 }
    ],
    activity_chart: [
      { date: '2024-01-01', messages: 45, chats: 8 },
      { date: '2024-01-02', messages: 67, chats: 12 },
      { date: '2024-01-03', messages: 34, chats: 6 },
      { date: '2024-01-04', messages: 89, chats: 15 },
      { date: '2024-01-05', messages: 123, chats: 18 }
    ]
  };

  const value: AppContextType = {
    apiConfig,
    updateApiConfig,
    managers,
    activeManager,
    setActiveManager: (m) => {
      setActiveManager(m);
      if (m && activeChat && activeChat.manager_id !== m.id) setActiveChat(null);
      if (!m) setActiveChat(null);
    },
    addManager,
    updateManager,
    deleteManager,
    chats,
    activeChat,
    setActiveChat,
    getChatsForManager,
    addChat,
    messages,
    sendMessage,
    accounts,
    addAccount,
    createAccountFromChat,
    getAccountByUserId,
    updateAccount,
    deleteAccount,
    chatSummaries,
    getChatSummary,
  analyticsData,
  transferRecords,
  addTransferRecord,
  updateTransferRecord,
  deleteTransferRecord,
  getTransfersByAccount,
    sidebarCollapsed,
    setSidebarCollapsed,
  sidebarOpen,
  setSidebarOpen,
    currentView,
    setCurrentView,
    chatMembers,
    getMembersForChat: (chatId: number) => chatMembers.filter(m => m.chat_id === chatId),
    addMembersBulk: (chatId: number, userIds: number[]) => {
      if (!userIds.length) return;
      setChatMembers(prev => {
        const existingSet = new Set(prev.filter(m => m.chat_id === chatId).map(m => m.user_id));
        const now = new Date().toISOString();
        const additions: ChatMember[] = userIds
          .filter(id => !existingSet.has(id))
          .map((id, idx) => ({
            chat_id: chatId,
            user_id: id,
            added_at: now,
            role: idx === 0 && prev.filter(m => m.chat_id === chatId).length === 0 ? 'creator' : 'member',
            user: {
              id,
              first_name: 'Имя'+id,
              last_name: 'Фамилия'+String(id).slice(-2),
              username: 'user_'+id,
              is_bot: false
            }
          }));
        const updated = [...prev, ...additions];
        localStorage.setItem('telegram_crm_chat_members', JSON.stringify(updated));
        return updated;
      });
    },
    keywords,
    setKeywords: (kw: string[]) => {
      const cleaned = kw.map(k => k.trim()).filter(Boolean).filter((v,i,a) => a.findIndex(x => x.toLowerCase() === v.toLowerCase()) === i);
      setKeywords(cleaned);
      localStorage.setItem('telegram_crm_keywords', JSON.stringify(cleaned));
    },

    // OpenRouter Balance
    balance,
    isLoadingBalance,
    loadBalance: async () => {
      setIsLoadingBalance(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/settings/openrouter/balance`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setBalance(data);
        } else {
          console.error('Failed to load balance');
        }
      } catch (error) {
        console.error('Error loading balance:', error);
      } finally {
        setIsLoadingBalance(false);
      }
    },

    // Business Accounts
    businessAccounts,
    activeBusinessAccount,
    setActiveBusinessAccount,
    isLoadingBusinessAccounts,
    loadBusinessAccounts: useCallback(async () => {
      setIsLoadingBusinessAccounts(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/business-accounts/`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setBusinessAccounts(data.accounts || []);
        } else if (response.status === 401) {
          console.warn('Authentication expired or invalid - redirecting to login');
          // Clear authentication state
          localStorage.removeItem('telegram_crm_logged_in');
          // Small delay to let user see the warning
          setTimeout(() => {
            window.location.reload();
          }, 1000);
          setBusinessAccounts([]);
        } else {
          console.error(`Failed to load business accounts: ${response.status} ${response.statusText}`);
          setBusinessAccounts([]);
        }
      } catch (error) {
        console.error('Error loading business accounts:', error);
        setBusinessAccounts([]);
      } finally {
        setIsLoadingBusinessAccounts(false);
      }
    }, []),

    // Business Chats
    businessChats,
    activeBusinessChat,
    setActiveBusinessChat,
    isLoadingBusinessChats,
    loadBusinessChats: useCallback(async (accountId: number) => {
      setIsLoadingBusinessChats(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/business-accounts/${accountId}/chats`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setBusinessChats(data.chats || []);
        } else {
          console.error('Failed to load business chats');
        }
      } catch (error) {
        console.error('Error loading business chats:', error);
      } finally {
        setIsLoadingBusinessChats(false);
      }
    }, []),

    // Business Messages
    businessMessages,
    isLoadingBusinessMessages,
    isSendingMessage,
    loadBusinessMessages: useCallback(async (chatId: number, limit = 50, offset = 0) => {
      setIsLoadingBusinessMessages(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/business-accounts/chats/${chatId}/messages?limit=${limit}&offset=${offset}`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (offset === 0) {
            setBusinessMessages(data.messages || []);
          } else {
            setBusinessMessages(prev => [...prev, ...(data.messages || [])]);
          }
        } else {
          console.error('Failed to load business messages');
        }
      } catch (error) {
        console.error('Error loading business messages:', error);
      } finally {
        setIsLoadingBusinessMessages(false);
      }
    }, []),

    sendBusinessMessage: useCallback(async (connectionId: string, chatId: number, text: string) => {
      setIsSendingMessage(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/business-accounts/send-message`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            business_connection_id: connectionId,
            chat_id: chatId,
            text: text
          }),
        });

        if (response.ok) {
          // Reload messages after sending
          if (activeBusinessChat) {
            const reloadResponse = await fetch(`${API_BASE_URL}/api/v1/business-accounts/chats/${activeBusinessChat.id}/messages?limit=50&offset=0`, {
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
              },
            });
            if (reloadResponse.ok) {
              const data = await reloadResponse.json();
              setBusinessMessages(data.messages || []);
            }
          }
        } else {
          console.error('Failed to send business message');
          throw new Error('Failed to send message');
        }
      } catch (error) {
        console.error('Error sending business message:', error);
        throw error;
      } finally {
        setIsSendingMessage(false);
      }
    }, [activeBusinessChat]),

    sendBusinessPhoto: useCallback(async (connectionId: string, chatId: number, fileId: string, caption?: string) => {
      setIsSendingMessage(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/business-accounts/send-photo`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            business_connection_id: connectionId,
            chat_id: chatId,
            photo_file_id: fileId,
            caption: caption
          }),
        });

        if (response.ok) {
          // Reload messages after sending
          if (activeBusinessChat) {
            const reloadResponse = await fetch(`${API_BASE_URL}/api/v1/business-accounts/chats/${activeBusinessChat.id}/messages?limit=50&offset=0`, {
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
              },
            });
            if (reloadResponse.ok) {
              const data = await reloadResponse.json();
              setBusinessMessages(data.messages || []);
            }
          }
        } else {
          console.error('Failed to send business photo');
          throw new Error('Failed to send photo');
        }
      } catch (error) {
        console.error('Error sending business photo:', error);
        throw error;
      } finally {
        setIsSendingMessage(false);
      }
    }, [activeBusinessChat]),

    sendBusinessDocument: useCallback(async (connectionId: string, chatId: number, fileId: string, caption?: string) => {
      setIsSendingMessage(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/business-accounts/send-document`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            business_connection_id: connectionId,
            chat_id: chatId,
            document_file_id: fileId,
            caption: caption
          }),
        });

        if (response.ok) {
          // Reload messages after sending
          if (activeBusinessChat) {
            const reloadResponse = await fetch(`${API_BASE_URL}/api/v1/business-accounts/chats/${activeBusinessChat.id}/messages?limit=50&offset=0`, {
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
              },
            });
            if (reloadResponse.ok) {
              const data = await reloadResponse.json();
              setBusinessMessages(data.messages || []);
            }
          }
        } else {
          console.error('Failed to send business document');
          throw new Error('Failed to send document');
        }
      } catch (error) {
        console.error('Error sending business document:', error);
        throw error;
      } finally {
        setIsSendingMessage(false);
      }
    }, [activeBusinessChat]),

    uploadFile: useCallback(async (file: File) => {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/v1/files/upload-to-telegram`, {
          method: 'POST',
          credentials: 'include',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          return {
            file_id: data.file_id,
            message_type: data.message_type
          };
        } else {
          console.error('Failed to upload file');
          throw new Error('Failed to upload file');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
      }
    }, [])
  };

  // Seed a second manager with its own distinct chats if only one manager exists
  React.useEffect(() => {
    if (
      managers.length === 1 &&
      chats.length > 0 &&
      chats.every(c => c.manager_id === managers[0].id) &&
      !localStorage.getItem('telegram_crm_two_managers_seeded')
    ) {
      const second = addManager('Менеджер 2');
      let maxId = chats.reduce((m, c) => Math.max(m, c.id), 0);
      const newChats: Chat[] = [
        {
          id: ++maxId,
          type: 'private',
          first_name: 'Алина',
          last_name: 'Ковалёва',
          username: 'alina_k',
          unread_count: 2,
            pinned: false,
            muted: false,
            is_bot_chat: true,
            manager_id: second.id,
            last_message: {
              id: maxId * 10 + 1,
              chat_id: maxId,
              sender_id: second.id,
              text: 'Добрый день! Отправила обновлённый документ.',
              date: Date.now(),
              from_me: false
            }
        },
        {
          id: ++maxId,
          type: 'private',
          first_name: 'Дмитрий',
          last_name: 'Петров',
          username: 'dpetrov',
          unread_count: 0,
          pinned: false,
          muted: false,
          is_bot_chat: true,
          manager_id: second.id,
          last_message: {
            id: maxId * 10 + 1,
            chat_id: maxId,
            sender_id: second.id,
            text: 'Спасибо, всё получил. Начинаю работу.',
            date: Date.now(),
            from_me: false
          }
        }
      ];
      setChats(prev => {
        const list = [...prev, ...newChats];
        localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(list));
        return list;
      });
      localStorage.setItem('telegram_crm_two_managers_seeded', '1');
    }
  }, [managers, chats, addManager]);

  // Repair / normalize legacy chats so manager_id always maps to an existing manager.
  React.useEffect(() => {
    if (!managers.length) return;
    const managerIds = new Set(managers.map(m => m.id));
    let changed = false;
    setChats(prev => {
      if (!prev.length) {
        const seeded = createMockChats(managers[0].id);
        localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(seeded));
        return seeded;
      }
      const normalized = prev.map((c: any) => {
        let mgrId = c.manager_id;
        if (typeof mgrId !== 'number' || !managerIds.has(mgrId)) {
          // Try legacy account_id if present and equals some manager id (unlikely), else fallback to first manager
          if (typeof c.account_id === 'number' && managerIds.has(c.account_id)) {
            mgrId = c.account_id;
          } else {
            mgrId = managers[0].id;
          }
          changed = true;
          return { ...c, manager_id: mgrId };
        }
        return c;
      });
      if (changed) {
        localStorage.setItem('telegram_crm_chats_v2', JSON.stringify(normalized));
        return normalized as Chat[];
      }
      return prev as Chat[];
    });
  }, [managers]);

  // Load chat members from storage
  useEffect(() => {
    const raw = localStorage.getItem('telegram_crm_chat_members');
    if (raw) {
      try { setChatMembers(JSON.parse(raw)); } catch {}
    } else {
      // Seed mock members for group chats with user snapshot
      const groupChats = chats.filter(c => c.type === 'group' || c.type === 'supergroup');
      if (groupChats.length) {
        const seeded: ChatMember[] = [];
        groupChats.forEach(gc => {
          for (let i = 0; i < 5; i++) {
            const uid = Number(`${gc.id}${i+1}`);
            seeded.push({
              chat_id: gc.id,
              user_id: uid,
              added_at: new Date().toISOString(),
              role: i === 0 ? 'creator' : (i <= 2 ? 'admin' : 'member'),
              user: {
                id: uid,
                first_name: ['Иван','Мария','Павел','Ольга','Сергей'][i % 5],
                last_name: ['Иванов','Петрова','Сидоров','Кузнецова','Смирнов'][i % 5],
                username: `user_${uid}`,
                is_bot: false,
                photo_url: undefined
              }
            });
          }
        });
        setChatMembers(seeded);
        localStorage.setItem('telegram_crm_chat_members', JSON.stringify(seeded));
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};