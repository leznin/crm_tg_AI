import React, { useEffect, useRef, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import { Send, ArrowLeft, Info, User, Paperclip, Image, FileText } from 'lucide-react';
import AccountModal from './AccountModal';
import { BusinessMessage } from '../types';

const BusinessChatWindow: React.FC = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const {
    businessAccounts,
    activeBusinessAccount,
    setActiveBusinessAccount,
    businessChats,
    activeBusinessChat,
    setActiveBusinessChat,
    businessMessages,
    loadBusinessAccounts,
    loadBusinessChats,
    loadBusinessMessages,
    sendBusinessMessage,
    sendBusinessPhoto,
    sendBusinessDocument,
    uploadFile,
    isLoadingBusinessAccounts,
    isLoadingBusinessChats,
    isLoadingBusinessMessages,
    isSendingMessage,
    setSidebarOpen,
    accounts,
    addAccount,
    updateAccount
  } = useAppContext();

  const [accountModalOpen, setAccountModalOpen] = useState(false);
  const [messageText, setMessageText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Load business accounts on component mount (only if authenticated and not loading)
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      loadBusinessAccounts().catch(error => {
        console.error('Failed to load business accounts:', error);
      });
    }
  }, [isAuthenticated, authLoading, loadBusinessAccounts]);

  // Load chats when business account changes
  useEffect(() => {
    if (activeBusinessAccount) {
      loadBusinessChats(activeBusinessAccount.id);
    }
  }, [activeBusinessAccount, loadBusinessChats]);

  // Load messages when business chat changes
  useEffect(() => {
    if (activeBusinessChat) {
      loadBusinessMessages(activeBusinessChat.id);
    }
  }, [activeBusinessChat, loadBusinessMessages]);

  // Focus input when chat changes
  useEffect(() => {
    if (activeBusinessChat && inputRef.current) {
      inputRef.current.focus();
    }
  }, [activeBusinessChat]);

  const handleSend = async () => {
    if (!activeBusinessAccount || !activeBusinessChat || (!messageText.trim() && !selectedFile)) return;

    try {
      if (selectedFile) {
        // Upload file and send
        const uploadResult = await uploadFile(selectedFile);
        if (uploadResult.message_type === 'photo') {
          await sendBusinessPhoto(
            activeBusinessAccount.business_connection_id,
            activeBusinessChat.chat_id,
            uploadResult.file_id,
            messageText.trim() || undefined
          );
        } else {
          await sendBusinessDocument(
            activeBusinessAccount.business_connection_id,
            activeBusinessChat.chat_id,
            uploadResult.file_id,
            messageText.trim() || undefined
          );
        }
        setSelectedFile(null);
      } else {
        // Send text message
        await sendBusinessMessage(
          activeBusinessAccount.business_connection_id,
          activeBusinessChat.chat_id,
          messageText.trim()
        );
      }
      setMessageText('');
    } catch (error) {
      console.error('Failed to send message:', error);
      // You might want to show an error toast here
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const getChatTitle = () => {
    if (!activeBusinessChat) return '';
    const name = [activeBusinessChat.first_name, activeBusinessChat.last_name].filter(Boolean).join(' ').trim();
    return activeBusinessChat.title || name || (activeBusinessChat.username ? '@' + activeBusinessChat.username : 'Без названия');
  };

  const formatMessageTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }
    
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  };

  const renderMessage = (message: BusinessMessage) => {
    const isOutgoing = message.is_outgoing;
    const senderName = message.sender_first_name || message.sender_username || 'Неизвестный';

    return (
      <div key={message.id} className={`flex ${isOutgoing ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isOutgoing 
            ? 'bg-blue-600 text-white' 
            : 'bg-surface-200 text-gray-200'
        }`}>
          {!isOutgoing && (
            <div className="text-xs text-gray-400 mb-1">{senderName}</div>
          )}
          
          {message.message_type === 'photo' && message.file_id && (
            <div className="mb-2">
              <div className="w-48 h-32 bg-gray-300 rounded flex items-center justify-center">
                <Image className="w-8 h-8 text-gray-500" />
                <span className="ml-2 text-sm text-gray-500">Фото</span>
              </div>
            </div>
          )}
          
          {message.message_type === 'document' && message.file_id && (
            <div className="mb-2 flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span className="text-sm">{message.file_name || 'Документ'}</span>
            </div>
          )}
          
          {message.text && (
            <div className="whitespace-pre-wrap break-words">{message.text}</div>
          )}
          
          <div className={`text-xs mt-1 ${isOutgoing ? 'text-blue-200' : 'text-gray-500'}`}>
            {formatMessageTime(message.telegram_date)}
          </div>
        </div>
      </div>
    );
  };

  // Show loading state while loading business accounts
  if (isLoadingBusinessAccounts) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-surface-50/40 backdrop-blur-md">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Загрузка бизнес-аккаунтов...</p>
        </div>
      </div>
    );
  }

  // Show message if no business accounts
  if (businessAccounts.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-surface-50/40 backdrop-blur-md">
        <div className="max-w-md text-center px-6">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">B</div>
          <h2 className="text-2xl font-bold text-gray-200 mb-3">Нет бизнес-аккаунтов</h2>
          <p className="text-gray-400 mb-6">Подключите Telegram Bot к бизнес-аккаунту для начала работы.</p>
        </div>
      </div>
    );
  }

  // Show message if no business account selected
  if (!activeBusinessAccount) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-surface-50/40 backdrop-blur-md">
        <div className="max-w-md text-center px-6">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">A</div>
          <h2 className="text-2xl font-bold text-gray-200 mb-3">Выберите бизнес-аккаунт</h2>
          <p className="text-gray-400 mb-6">Выберите бизнес-аккаунт слева для просмотра диалогов.</p>
        </div>
      </div>
    );
  }

  // Show message if no chat selected
  if (!activeBusinessChat) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-surface-50/40 backdrop-blur-md">
        <div className="max-w-md text-center px-6">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">C</div>
          <h2 className="text-2xl font-bold text-gray-200 mb-3">Выберите диалог</h2>
          <p className="text-gray-400 mb-6">Выберите диалог из списка для просмотра сообщений.</p>
          {businessChats.length === 0 && (
            <p className="text-sm text-gray-500">Пока нет диалогов в этом бизнес-аккаунте.</p>
          )}
        </div>
      </div>
    );
  }

  const existingAccount = accounts.find(a => a.user_id === activeBusinessChat.sender_id);

  return (
    <>
      <div className="flex-1 flex flex-col bg-surface-50/60 backdrop-blur-md overflow-hidden border-l border-white/5">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-surface-100/60 backdrop-blur-sm">
          <div className="flex items-center space-x-3 min-w-0">
            <button
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5"
              onClick={() => { setSidebarOpen(true); setActiveBusinessChat(null); }}
              aria-label="Назад к списку чатов"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-inner-glow">
              <span className="text-white font-semibold text-sm">{getChatTitle().charAt(0).toUpperCase()}</span>
            </div>
            <div className="min-w-0">
              <h2 className="font-semibold text-gray-100 truncate max-w-xs md:max-w-md text-sm tracking-wide">{getChatTitle()}</h2>
              {activeBusinessChat?.username && (<p className="text-[10px] text-gray-500 truncate">@{activeBusinessChat.username}</p>)}
              <p className="text-[10px] text-blue-400">Бизнес-аккаунт: {activeBusinessAccount.first_name}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              className="relative p-2 rounded-lg text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-blue-500/60 transition-colors"
              onClick={() => setAccountModalOpen(true)}
              aria-label="Карточка клиента"
            >
              <User className="w-5 h-5" />
              {activeBusinessChat.unread_count > 0 && (
                <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_0_2px_rgba(0,0,0,0.5)] animate-pulse" />
              )}
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoadingBusinessMessages ? (
            <div className="flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : businessMessages.length === 0 ? (
            <div className="flex justify-center items-center h-full">
              <p className="text-gray-400">Нет сообщений</p>
            </div>
          ) : (
            <div className="space-y-4">
              {businessMessages.slice().reverse().map(renderMessage)}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-white/5 p-4 bg-surface-100/40 backdrop-blur-md">
          {selectedFile && (
            <div className="mb-3 p-2 bg-surface-200/40 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-gray-300">{selectedFile.name}</span>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-gray-400 hover:text-white"
              >
                ×
              </button>
            </div>
          )}
          
          <div className="flex items-end space-x-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*,.pdf,.doc,.docx,.txt"
              className="hidden"
            />
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
              aria-label="Прикрепить файл"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={selectedFile ? "Добавьте подпись..." : "Введите сообщение..."}
                rows={1}
                className="w-full resize-none pr-12 p-3 rounded-lg bg-surface-200/40 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 transition-colors text-sm placeholder:text-gray-500 text-gray-200"
              />
              <div className="absolute right-3 bottom-3 flex items-center space-x-2">
                <span className="text-[10px] text-gray-500 tracking-wide">Enter — отправить</span>
              </div>
            </div>
            
            <button
              onClick={handleSend}
              disabled={(!messageText.trim() && !selectedFile) || isSendingMessage}
              className="h-11 px-5 rounded-lg flex items-center space-x-2 font-medium bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-sm shadow-glow-blue"
            >
              {isSendingMessage ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Send className="w-4 h-4" />
              )}
              <span className="hidden sm:inline">
                {isSendingMessage ? 'Отправка...' : 'Отправить'}
              </span>
            </button>
          </div>
        </div>
      </div>

      <AccountModal
        isOpen={accountModalOpen}
        onClose={() => setAccountModalOpen(false)}
        editingAccount={existingAccount || undefined}
        onCreate={(data) => { addAccount({ ...data, manager_id: data.manager_id }); setAccountModalOpen(false); }}
        onUpdate={(id, updates) => { updateAccount(id, updates); setAccountModalOpen(false); }}
        initialChat={!existingAccount ? {
          id: activeBusinessChat.chat_id,
          type: activeBusinessChat.chat_type as any,
          title: activeBusinessChat.title,
          first_name: activeBusinessChat.first_name,
          last_name: activeBusinessChat.last_name,
          username: activeBusinessChat.username,
          unread_count: activeBusinessChat.unread_count,
          pinned: false,
          muted: false,
          is_bot_chat: true,
          manager_id: 0
        } : undefined}
      />
    </>
  );
};

export default BusinessChatWindow;
