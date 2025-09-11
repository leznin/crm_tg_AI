import React, { useMemo, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Upload, Users, Hash, UserPlus, MessageSquare, X } from 'lucide-react';

// Utility: derive display title for chat
const chatTitle = (chat: any) => chat.title || `${chat.first_name || ''} ${chat.last_name || ''}`.trim() || chat.username || 'Без названия';

const BotChatsAdmin: React.FC = () => {
  const { chats, getMembersForChat, addMembersBulk, activeManager, messages, keywords } = useAppContext();
  const [expandedChatId, setExpandedChatId] = useState<number | null>(null);
  const [uploadingChatId, setUploadingChatId] = useState<number | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [keywordModal, setKeywordModal] = useState<{ chatId: number; userId?: number | null; list: typeof messages } | null>(null);

  const loweredKeywords = useMemo(() => keywords.map(k => k.toLowerCase()).filter(Boolean), [keywords]);

  const buildIndex = useMemo(() => {
    if (!loweredKeywords.length) return new Map<number, Map<number, typeof messages>>();
    const map = new Map<number, Map<number, typeof messages>>();
    // Собираем массив сообщений: реальные + last_message из чатов (если её нет среди реальных)
    const synthetic = chats
      .map(c => c.last_message)
      .filter((m): m is typeof messages[number] => !!m && !!m.text && !messages.some(r => r.id === m.id));
    const all = [...messages, ...synthetic];
    for (const m of all) {
      if (!m.text) continue;
      const txt = m.text.toLowerCase();
      if (!loweredKeywords.some(k => txt.includes(k))) continue;
      if (!map.has(m.chat_id)) map.set(m.chat_id, new Map());
      const chatMap = map.get(m.chat_id)!;
      if (!chatMap.has(m.sender_id)) chatMap.set(m.sender_id, [] as typeof messages);
      chatMap.get(m.sender_id)!.push(m);
    }
    return map;
  }, [messages, loweredKeywords, chats]);

  const highlight = (text: string) => {
    if (!loweredKeywords.length) return text;
    // Escape regex special chars in keywords
    const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp('(' + loweredKeywords.map(esc).join('|') + ')', 'ig');
    const parts = text.split(pattern);
    return parts.map((p, i) => pattern.test(p.toLowerCase()) ? (
      <mark key={i} className="bg-amber-500/30 text-amber-200 rounded px-0.5">{p}</mark>
    ) : <span key={i}>{p}</span>);
  };

  // Chats where bot is admin (mock flag is_bot_chat used) and type group/supergroup/channel
  const adminChats = chats.filter(c => c.is_bot_chat && ['group','supergroup','channel'].includes(c.type));
  const filtered = adminChats.filter(c => chatTitle(c).toLowerCase().includes(search.toLowerCase()));

  const handleFile = (chatId: number, file: File) => {
    setUploadingChatId(chatId);
    setUploadError(null);
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const text = String(reader.result || '');
        // Accept separators: newline, comma, space
        const tokens = text.split(/[,\n\r\t\s]+/).map(t => t.trim()).filter(Boolean);
        const ids = tokens.map(t => Number(t)).filter(n => Number.isFinite(n) && n > 0);
        if (!ids.length) throw new Error('Не найдено корректных ID');
        addMembersBulk(chatId, ids);
      } catch (e: any) {
        setUploadError(e.message || 'Ошибка разбора файла');
      } finally {
        setUploadingChatId(null);
      }
    };
    reader.onerror = () => { setUploadError('Ошибка чтения файла'); setUploadingChatId(null); };
    reader.readAsText(file);
  };

  return (
    <div className="p-6 overflow-y-auto flex-1">
      <div className="flex flex-col lg:flex-row lg:items-center gap-4 mb-6">
        <h2 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-300 to-indigo-300">Группы / Каналы бота</h2>
        <div className="flex-1" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Поиск чата..." className="h-10 w-full lg:w-72 px-4 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 text-sm" />
      </div>

      {activeManager && (
        <div className="mb-4 text-xs text-gray-400">Активный менеджер: <span className="text-gray-200 font-medium">{activeManager.name}</span></div>
      )}

      {filtered.length === 0 && (
        <div className="text-sm text-gray-500">Нет групп/каналов где бот админ.</div>
      )}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {filtered.map(chat => {
          const members = getMembersForChat(chat.id);
          const last = chat.last_message;
          const chatUserMap = buildIndex.get(chat.id);
          const chatMatchCount = chatUserMap ? Array.from(chatUserMap.values()).reduce((acc, arr) => acc + arr.length, 0) : 0;
          return (
            <div key={chat.id} className="group relative rounded-xl border border-white/5 bg-surface-50/40 backdrop-blur-sm p-5 shadow-elevated-sm hover:shadow-elevated transition">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-600 via-blue-600 to-cyan-600 flex items-center justify-center font-semibold text-white text-lg">{chatTitle(chat).charAt(0).toUpperCase()}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-sm text-gray-100 truncate" title={chatTitle(chat)}>{chatTitle(chat)}</h3>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-600/30 text-blue-300 border border-blue-500/30 uppercase tracking-wide">{chat.type}</span>
                    {chatMatchCount > 0 && (
                      <button
                        type="button"
                        onClick={() => {
                          const all = chatUserMap ? Array.from(chatUserMap.values()).flat().slice().sort((a,b)=>b.date-a.date) : [];
                          setKeywordModal({ chatId: chat.id, userId: null, list: all });
                        }}
                        title="Все сообщения с ключевыми словами в этом чате"
                        className="text-[10px] px-2 py-0.5 rounded-full bg-amber-600/30 hover:bg-amber-600/40 text-amber-200 border border-amber-500/30 font-medium tracking-wide focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                      >KW {chatMatchCount}</button>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-gray-400">
                    <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {members.length}</span>
                    {last && (<span>Сообщение: {new Date(last.date).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'})}</span>)}
                    {chat.unread_count > 0 && <span className="text-emerald-400">Непрочитанных: {chat.unread_count}</span>}
                  </div>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-3">
                <label className="inline-flex items-center gap-2 text-xs px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer text-gray-300">
                  <Upload className="w-4 h-4" /> Загрузить ID
                  <input disabled={uploadingChatId===chat.id} type="file" accept=".txt" className="hidden" onChange={e => { const f=e.target.files?.[0]; if (f) handleFile(chat.id,f); e.target.value=''; }} />
                </label>
                <button onClick={() => setExpandedChatId(expandedChatId === chat.id ? null : chat.id)} className="text-xs px-3 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-500 hover:to-indigo-500">
                  {expandedChatId === chat.id ? 'Скрыть' : 'Участники'}
                </button>
              </div>
              {uploadingChatId === chat.id && <div className="mt-2 text-[11px] text-blue-300 animate-pulse">Обработка файла...</div>}
              {uploadError && <div className="mt-2 text-[11px] text-red-400">{uploadError}</div>}

              {expandedChatId === chat.id && (
                <div className="mt-4 border-t border-white/5 pt-3 max-h-56 overflow-y-auto pr-1">
                  {members.length === 0 && <div className="text-[11px] text-gray-500">Нет участников</div>}
                  <ul className="space-y-1">
                    {members.map(m => {
                      const u = m.user;
                      const matched = buildIndex.get(chat.id)?.get(m.user_id) || [];
                      return (
                        <li key={m.chat_id+':'+m.user_id} className="text-[11px] bg-white/5 rounded-md px-2 py-1">
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 min-w-0">
                              <Hash className="w-3 h-3 text-gray-500 flex-shrink-0" />
                              <span className="text-gray-300 truncate">{m.user_id}</span>
                              {u?.username && <span className="text-gray-500 truncate">@{u.username}</span>}
                            </div>
                            <div className="flex items-center gap-1 flex-shrink-0">
                              {!!matched.length && (
                                <button
                                  onClick={() => setKeywordModal({ chatId: chat.id, userId: m.user_id, list: matched.slice().sort((a,b)=>b.date-a.date) })}
                                  className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-200 hover:bg-amber-500/30 flex items-center gap-1"
                                  title="Сообщения с ключевыми словами"
                                >
                                  <MessageSquare className="w-3 h-3" />
                                  <span className="text-[10px] font-medium leading-none">{matched.length}</span>
                                </button>
                              )}
                              {m.role && <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 uppercase tracking-wide text-[9px]">{m.role}</span>}
                            </div>
                          </div>
                          {u && (
                            <div className="mt-0.5 text-gray-400 flex flex-wrap gap-x-3 gap-y-0.5">
                              <span>{u.first_name} {u.last_name}</span>
                              <span className="text-[10px]">{u.is_bot ? 'бот' : 'user'}</span>
                            </div>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-10 text-[11px] text-gray-500 space-y-2">
        <p className="flex items-start gap-2"><UserPlus className="w-3.5 h-3.5 mt-0.5 text-gray-400" /> Загрузка .txt: перечислите ID пользователей (каждый в новой строке, через пробел или запятую). Данные сохраняются в вашей сессии.</p>
      </div>

      {keywordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setKeywordModal(null)} />
          <div className="relative w-full max-w-lg max-h-[80vh] overflow-hidden rounded-xl bg-surface-50/80 backdrop-blur-md border border-white/10 shadow-2xl flex flex-col">
            <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
              <h4 className="text-sm font-semibold text-gray-100">
                {keywordModal.userId ? (
                  <>Сообщения пользователя {keywordModal.userId}</>
                ) : (
                  <>Сообщения чата (ключевые)</>
                )}
              </h4>
              <button onClick={() => setKeywordModal(null)} className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5" aria-label="Закрыть">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="px-5 pt-2 pb-1 text-[10px] text-gray-400 flex items-center justify-between border-b border-white/5">
              <span>Всего сообщений: {keywordModal.list.length}</span>
              <span>Уникальных пользователей: {new Set(keywordModal.list.map(m => m.sender_id)).size}</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 text-[11px]">
              {keywordModal.list.map(msg => (
                <div key={msg.id} className="p-2 rounded-md bg-white/5 border border-white/5">
                  <div className="flex items-center justify-between mb-1 text-[10px] text-gray-500">
                    <span>{new Date(msg.date).toLocaleString('ru-RU',{hour:'2-digit',minute:'2-digit', day:'2-digit', month:'2-digit'})}</span>
                    <span className="text-[9px] text-amber-300">ID {msg.id}</span>
                  </div>
                  <div className="text-gray-300 leading-snug break-words">{highlight(msg.text)}</div>
                </div>
              ))}
              {!keywordModal.list.length && (
                <div className="text-gray-500">Нет сообщений</div>
              )}
            </div>
            <div className="p-3 border-t border-white/5 flex justify-end">
              <button onClick={() => setKeywordModal(null)} className="px-4 py-2 rounded-lg bg-surface-100/60 hover:bg-surface-100/80 text-xs text-gray-300">Закрыть</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BotChatsAdmin;
