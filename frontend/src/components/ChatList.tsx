import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Search, Pin, VolumeX, MoreVertical, Plus, User, X } from 'lucide-react';

const ChatList: React.FC = () => {
  const { chats, activeChat, setActiveChat, managers, activeManager, setActiveManager, addManager } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [addingManager, setAddingManager] = useState(false);
  const [newManagerName, setNewManagerName] = useState('');

  const managerChats = activeManager ? chats.filter(c => c.manager_id === activeManager.id) : [];

  const filteredChats = managerChats.filter(chat => {
    const searchLower = searchTerm.toLowerCase();
    const title = chat.title || `${chat.first_name || ''} ${chat.last_name || ''}`.trim();
    const username = chat.username || '';
    
    return title.toLowerCase().includes(searchLower) || 
           username.toLowerCase().includes(searchLower);
  });

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }
    
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full text-gray-200">
      {/* Manager Selector & Search */}
      <div className="p-4 border-b border-white/5 space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold tracking-wide text-gray-400 uppercase">Менеджер</h3>
            {!addingManager && (
              <button onClick={() => setAddingManager(true)} className="p-1.5 rounded-md bg-white/5 hover:bg-white/10 text-gray-300" aria-label="Добавить менеджера">
                <Plus className="w-4 h-4" />
              </button>
            )}
          </div>
          {addingManager ? (
            <form onSubmit={e => { e.preventDefault(); if (!newManagerName.trim()) return; const m = addManager(newManagerName.trim()); setActiveManager(m); setNewManagerName(''); setAddingManager(false); }} className="flex items-center gap-2">
              <input value={newManagerName} onChange={e => setNewManagerName(e.target.value)} autoFocus placeholder="Имя менеджера" className="flex-1 h-9 px-3 rounded-lg bg-surface-100/70 border border-white/5 text-sm focus:ring-2 focus:ring-blue-500/60" />
              <button type="submit" className="h-9 px-3 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-medium">OK</button>
              <button type="button" onClick={() => { setAddingManager(false); setNewManagerName(''); }} className="h-9 px-2 rounded-lg bg-white/5 text-gray-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </form>
          ) : (
            <div className="flex flex-wrap gap-2">
              {managers.map(m => (
                <button key={m.id} onClick={() => { setActiveManager(m); setActiveChat(null); }} className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-[11px] border transition-colors ${activeManager?.id === m.id ? 'bg-gradient-to-r from-blue-600 to-indigo-600 border-blue-500/60 text-white shadow-glow-blue' : 'bg-surface-100/60 border-white/10 text-gray-300 hover:bg-white/10'}`}> <User className="w-3.5 h-3.5" /> {m.name}</button>
              ))}
              {managers.length === 0 && (
                <span className="text-[11px] text-gray-500">Нет менеджеров</span>
              )}
            </div>
          )}
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
          <input
            type="text"
            placeholder="Поиск чатов..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-surface-100/70 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 transition-colors placeholder:text-gray-500 text-sm"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {!activeManager && (
          <div className="p-6 text-center text-xs text-gray-500 space-y-3">
            <p>Чтобы увидеть чаты, добавьте или выберите менеджера.</p>
          </div>
        )}
        {activeManager && filteredChats.length === 0 && (
          <div className="p-6 text-center text-[11px] text-gray-500">Нет чатов для этого менеджера.</div>
        )}
        {filteredChats.map(chat => {
          const title = chat.title || `${chat.first_name || ''} ${chat.last_name || ''}`.trim();
          const isActive = activeChat?.id === chat.id;
          
          return (
            <div
              key={chat.id}
              onClick={() => setActiveChat(chat)}
              className={`p-4 border-b border-white/5 cursor-pointer transition-colors duration-200 group ${
                isActive ? 'bg-surface-200/40 backdrop-blur-sm border-l-4 border-l-blue-500/80' : 'hover:bg-surface-100/50'
              }`}
            >
              <div className="flex items-start space-x-3">
                {/* Avatar */}
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-inner-glow">
                  <span className="text-white font-semibold text-base">
                    {title.charAt(0).toUpperCase()}
                  </span>
                </div>

                <div className="flex-1 min-w-0">
                  {/* Chat Title */}
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2">
                      <h3 className={`font-medium truncate text-sm ${isActive ? 'text-blue-300' : 'text-gray-200 group-hover:text-white'}`}>
                        {title}
                      </h3>
                      {chat.pinned && <Pin className="w-4 h-4 text-gray-500" />}
                      {chat.muted && <VolumeX className="w-4 h-4 text-gray-500" />}
                    </div>
                    <div className="flex items-center space-x-1">
                      {chat.last_message && (
                        <span className="text-[10px] tracking-wide text-gray-400">
                          {formatTime(chat.last_message.date)}
                        </span>
                      )}
                      <button className="p-1 hover:bg-white/5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity">
                        <MoreVertical className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                  </div>

                  {/* Last Message */}
                  {chat.last_message && (
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-gray-400 truncate">
                        {chat.last_message.from_me && (
                          <span className="text-blue-400 mr-1">Вы:</span>
                        )}
                        {chat.last_message.text}
                      </p>
                      
                      {chat.unread_count > 0 && (
                        <span className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white text-[10px] rounded-full px-2 py-1 ml-2 flex-shrink-0 shadow-glow-blue">
                          {chat.unread_count > 99 ? '99+' : chat.unread_count}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Username */}
                  {chat.username && (
                    <p className="text-[10px] text-gray-500 mt-1">@{chat.username}</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
  {/* AccountModal removed in manager-based UI */}
    </div>
  );
};

export default ChatList;