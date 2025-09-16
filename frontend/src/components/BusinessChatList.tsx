import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Search, User, MessageCircle, Clock, CheckCircle, XCircle } from 'lucide-react';
import { BusinessAccount, BusinessChat } from '../types';

const BusinessChatList: React.FC = () => {
  const {
    businessAccounts,
    activeBusinessAccount,
    setActiveBusinessAccount,
    businessChats,
    activeBusinessChat,
    setActiveBusinessChat,
    loadBusinessChats,
    isLoadingBusinessAccounts,
    isLoadingBusinessChats
  } = useAppContext();

  const [searchTerm, setSearchTerm] = useState('');

  const handleAccountSelect = async (account: BusinessAccount) => {
    setActiveBusinessAccount(account);
    setActiveBusinessChat(null); // Clear active chat when switching accounts
    await loadBusinessChats(account.id);
  };

  const handleChatSelect = (chat: BusinessChat) => {
    setActiveBusinessChat(chat);
  };

  const filteredChats = businessChats.filter(chat => {
    const searchLower = searchTerm.toLowerCase();
    const title = chat.title || `${chat.first_name || ''} ${chat.last_name || ''}`.trim();
    const username = chat.username || '';
    
    return title.toLowerCase().includes(searchLower) || 
           username.toLowerCase().includes(searchLower);
  });

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }
    
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  };

  const getChatTitle = (chat: BusinessChat) => {
    const name = [chat.first_name, chat.last_name].filter(Boolean).join(' ').trim();
    return chat.title || name || (chat.username ? '@' + chat.username : 'Без названия');
  };

  const getAccountDisplayName = (account: BusinessAccount) => {
    const name = [account.first_name, account.last_name].filter(Boolean).join(' ').trim();
    return name || account.username || 'Бизнес-аккаунт';
  };

  return (
    <div className="flex flex-col h-full text-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-white/5">
        <h1 className="text-lg font-semibold text-gray-100 mb-3">Бизнес-аккаунты</h1>
        
        {/* Search */}
        {activeBusinessAccount && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Поиск диалогов..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-surface-200/40 border border-white/5 rounded-lg focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 transition-colors text-sm placeholder:text-gray-500 text-gray-200"
            />
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoadingBusinessAccounts && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <p className="text-sm text-gray-400">Загрузка...</p>
          </div>
        </div>
      )}

      {/* Business Accounts List */}
      {!isLoadingBusinessAccounts && !activeBusinessAccount && (
        <div className="flex-1 overflow-y-auto">
          {businessAccounts.length === 0 ? (
            <div className="p-4 text-center">
              <p className="text-gray-400 text-sm">Нет подключенных бизнес-аккаунтов</p>
            </div>
          ) : (
            <div className="p-2">
              {businessAccounts.map((account) => (
                <button
                  key={account.id}
                  onClick={() => handleAccountSelect(account)}
                  className="w-full p-3 rounded-lg hover:bg-surface-100/40 transition-colors text-left mb-2"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-gray-100 truncate text-sm">
                          {getAccountDisplayName(account)}
                        </h3>
                        {account.is_enabled ? (
                          <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                        )}
                      </div>
                      {account.username && (
                        <p className="text-xs text-gray-500 truncate">@{account.username}</p>
                      )}
                      <p className="text-xs text-gray-500">
                        {account.is_enabled ? 'Активен' : 'Отключен'}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Business Chats List */}
      {activeBusinessAccount && (
        <>
          {/* Account Header */}
          <div className="p-3 border-b border-white/5 bg-surface-100/20">
            <button
              onClick={() => {
                setActiveBusinessAccount(null);
                setActiveBusinessChat(null);
              }}
              className="w-full text-left hover:bg-surface-100/40 rounded-lg p-2 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-100">
                    {getAccountDisplayName(activeBusinessAccount)}
                  </p>
                  <p className="text-xs text-gray-500">← Назад к списку аккаунтов</p>
                </div>
              </div>
            </button>
          </div>

          {/* Chats Loading */}
          {isLoadingBusinessChats && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
                <p className="text-sm text-gray-400">Загрузка диалогов...</p>
              </div>
            </div>
          )}

          {/* Chats List */}
          {!isLoadingBusinessChats && (
            <div className="flex-1 overflow-y-auto">
              {filteredChats.length === 0 ? (
                <div className="p-4 text-center">
                  <p className="text-gray-400 text-sm">
                    {searchTerm ? 'Диалоги не найдены' : 'Нет диалогов'}
                  </p>
                </div>
              ) : (
                <div className="p-2">
                  {filteredChats.map((chat) => (
                    <button
                      key={chat.id}
                      onClick={() => handleChatSelect(chat)}
                      className={`w-full p-3 rounded-lg transition-colors text-left mb-1 ${
                        activeBusinessChat?.id === chat.id
                          ? 'bg-blue-600/20 border border-blue-500/30'
                          : 'hover:bg-surface-100/40'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-xl flex items-center justify-center flex-shrink-0">
                          <span className="text-white font-semibold text-sm">
                            {getChatTitle(chat).charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h3 className="font-medium text-gray-100 truncate text-sm">
                              {getChatTitle(chat)}
                            </h3>
                            <div className="flex items-center space-x-2 flex-shrink-0">
                              {chat.last_message_at && (
                                <span className="text-xs text-gray-500">
                                  {formatTime(chat.last_message_at)}
                                </span>
                              )}
                              {chat.unread_count > 0 && (
                                <span className="bg-blue-500 text-white text-xs rounded-full px-2 py-0.5 min-w-[1.25rem] text-center">
                                  {chat.unread_count > 99 ? '99+' : chat.unread_count}
                                </span>
                              )}
                            </div>
                          </div>
                          {chat.username && (
                            <p className="text-xs text-gray-500 truncate">@{chat.username}</p>
                          )}
                          {chat.last_message && (
                            <p className="text-xs text-gray-400 truncate mt-1">
                              {chat.last_message.text || `${chat.last_message.message_type} сообщение`}
                            </p>
                          )}
                          <div className="flex items-center space-x-3 mt-1">
                            <div className="flex items-center space-x-1">
                              <MessageCircle className="w-3 h-3 text-gray-500" />
                              <span className="text-xs text-gray-500">{chat.message_count}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="w-3 h-3 text-gray-500" />
                              <span className="text-xs text-gray-500 capitalize">{chat.chat_type}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default BusinessChatList;


