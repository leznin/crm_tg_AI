import React, { useEffect, useState, useCallback } from 'react';
import { Account, Chat } from '../types';
import { useAppContext } from '../context/AppContext';
import { X, User, AtSign, Star, Hash, FileText, Sparkles } from 'lucide-react';

interface AccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  editingAccount?: Account | null;
  onCreate: (accountData: Omit<Account, 'id'>) => Promise<void>;
  onUpdate: (id: number, updates: Omit<Account, 'id'>) => Promise<void>;
  initialChat?: Chat; // Used when opened from a chat to prefill
}

interface FormData {
  first_name: string; // Может быть пустым, будем выводить fallback
  last_name: string;
  username: string;
  rating: number;
  category: Account['category'];
  source: Account['source'];
  tags: string;
  notes: string;
  registration_date: string; // YYYY-MM-DD
  brand_name: string;
  position: string;
  years_in_market: string; // keep as string for controlled input, convert to number
  business_account_id?: number;
}

const defaultForm: FormData = {
  first_name: '',
  last_name: '',
  username: '',
  // Default rating changed to 1 star
  rating: 1,
  category: 'lead',
  source: 'private',
  tags: '',
  notes: '',
  registration_date: '',
  brand_name: '',
  position: '',
  years_in_market: ''
};

const AccountModal: React.FC<AccountModalProps> = ({
  isOpen,
  onClose,
  editingAccount,
  onCreate,
  onUpdate,
  initialChat
}) => {
  const { businessAccounts, activeBusinessAccount } = useAppContext();
  const [formData, setFormData] = useState<FormData>(defaultForm);
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);

  // Derived compact heading
  const isEdit = Boolean(editingAccount);

  // Initialize form when modal opens
  useEffect(() => {
    if (!isOpen) return;
    if (editingAccount) {
      setFormData({
        first_name: editingAccount.first_name,
        last_name: editingAccount.last_name || '',
        username: editingAccount.username || '',
        rating: editingAccount.rating,
        category: editingAccount.category,
        source: editingAccount.source,
        tags: editingAccount.tags.join(', '),
  notes: editingAccount.notes,
  registration_date: editingAccount.registration_date ? editingAccount.registration_date.slice(0,10) : '',
  brand_name: editingAccount.brand_name || '',
  position: editingAccount.position || '',
  years_in_market: editingAccount.years_in_market?.toString() || '',
  business_account_id: editingAccount.manager_id || activeBusinessAccount?.id
      });
      setTags(editingAccount.tags);
    } else if (initialChat) {
      setFormData({
        first_name: initialChat.first_name || initialChat.title || initialChat.username || '',
        last_name: initialChat.last_name || '',
        username: initialChat.username || '',
        rating: 1,
        category: initialChat.type === 'private' ? 'lead' : 'other',
        source: initialChat.type === 'private' ? 'private' : 'group',
        tags: '',
  notes: `Автоматически создан из ${initialChat.type === 'private' ? 'личного' : 'группового'} чата`,
  registration_date: '',
  brand_name: '',
  position: '',
  years_in_market: '',
  business_account_id: activeBusinessAccount?.id
      });
      setTags([]);
    } else {
      setFormData(defaultForm);
      setTags([]);
    }
    setTagInput('');
  }, [isOpen, editingAccount, initialChat]);

  // Close on ESC
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  const commitTag = useCallback((raw?: string) => {
    const value = (raw ?? tagInput).trim();
    if (!value) return;
    if (!tags.includes(value)) setTags(prev => [...prev, value]);
    setTagInput('');
  }, [tagInput, tags]);

  const removeTag = (t: string) => setTags(prev => prev.filter(x => x !== t));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Определяем финальное имя: при отсутствии берём username или 'Без имени'
    const resolvedFirstName = (formData.first_name || formData.username || 'Без имени').trim();
    const base: Omit<Account, 'id'> = {
      user_id: editingAccount?.user_id || Date.now(),
      first_name: resolvedFirstName,
      last_name: formData.last_name?.trim() || undefined,
      username: formData.username.trim() || undefined,
      rating: formData.rating,
      category: formData.category,
      source: formData.source,
      tags: tags.length ? tags : formData.tags.split(',').map(t => t.trim()).filter(Boolean),
      notes: formData.notes,
      created_at: editingAccount?.created_at || new Date().toISOString(),
      last_contact: new Date().toISOString(),
      total_messages: editingAccount?.total_messages || 0,
  chat_type: initialChat?.type || editingAccount?.chat_type,
  registration_date: formData.registration_date || editingAccount?.registration_date,
  brand_name: formData.brand_name.trim() || editingAccount?.brand_name,
  position: formData.position.trim() || editingAccount?.position,
  years_in_market: formData.years_in_market ? Number(formData.years_in_market) : editingAccount?.years_in_market
  ,manager_id: formData.business_account_id || activeBusinessAccount?.id
    };
    
    try {
      if (editingAccount) {
        await onUpdate(editingAccount.id, base);
      } else {
        await onCreate(base);
      }
      onClose();
    } catch (error) {
      console.error('Error saving account:', error);
      // Не закрываем модал при ошибке, чтобы пользователь мог попробовать снова
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center sm:items-center p-4 overflow-y-auto text-gray-200">
      {/* Backdrop */}
  <div className="fixed inset-0 bg-black/60 backdrop-blur-md animate-fade-in" onClick={onClose} />
  <div className="relative w-full max-w-lg bg-surface-50/80 backdrop-blur-xl border border-white/10 shadow-elevated-lg rounded-2xl p-5 sm:p-7 my-8 animate-scale-in">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-gray-100 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              {isEdit ? 'Редактировать аккаунт' : 'Новый аккаунт'}
            </h2>
            <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-wide">Минимум полей — максимум контекста</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center rounded-full hover:bg-white/5 text-gray-400 hover:text-gray-200 transition-colors"
            aria-label="Закрыть"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Business Account Selection */}
          <div>
            <label className="text-[10px] font-medium text-gray-400 mb-1 flex items-center gap-1">Бизнес-аккаунт (на который написал пользователь)</label>
            <select
              value={formData.business_account_id || ''}
              onChange={e => setFormData({ ...formData, business_account_id: e.target.value ? Number(e.target.value) : undefined })}
              className="w-full h-11 pl-3 pr-8 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 appearance-none"
            >
              <option value="">— Не выбран —</option>
              {businessAccounts.map(ba => (
                <option key={ba.id} value={ba.id}>
                  {ba.first_name} {ba.last_name} {ba.username ? `(@${ba.username})` : ''}
                </option>
              ))}
            </select>
            {editingAccount?.manager_id && !formData.business_account_id && (
              <p className="mt-1 text-[10px] text-amber-400">У контакта был привязан бизнес-аккаунт, подтвердите или выберите новый.</p>
            )}
            {!businessAccounts.length && (
              <p className="mt-1 text-[10px] text-red-400">Нет бизнес-аккаунтов — сначала настройте Telegram Business.</p>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* First Name */}
            <div>
              <label className="text-[10px] font-medium text-gray-400 mb-1 flex items-center gap-1"><User className="w-3.5 h-3.5 text-gray-500" />Имя</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                placeholder="Имя (опционально)"
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all placeholder:text-gray-500"
              />
            </div>
            {/* Last Name */}
            <div>
              <label className="text-[10px] font-medium text-gray-400 mb-1 flex items-center gap-1"><User className="w-3.5 h-3.5 text-gray-500" />Фамилия</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                placeholder="Фамилия"
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all placeholder:text-gray-500"
              />
            </div>
            {/* Username */}
            <div className="sm:col-span-2">
              <label className="text-[10px] font-medium text-gray-400 mb-1 flex items-center gap-1"><AtSign className="w-3.5 h-3.5 text-gray-500" />Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={e => setFormData({ ...formData, username: e.target.value })}
                placeholder="@username (опционально)"
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all placeholder:text-gray-500"
              />
              {editingAccount?.username_history?.length ? (
                <p className="mt-1 text-[10px] leading-relaxed text-gray-500">
                  История: {editingAccount.username_history.map(h => `${h.username} (${new Date(h.changed_at).toLocaleDateString()})`).join(', ')}
                </p>
              ) : null}
            </div>
            {/* Rating */}
            <div className="sm:col-span-2">
              <span className="block text-[10px] font-medium text-gray-400 mb-1">Рейтинг</span>
              <div className="flex items-center gap-1">
                {[1,2,3,4,5].map(num => (
                  <button
                    type="button"
                    key={num}
                    onClick={() => setFormData({ ...formData, rating: num })}
                    className={`p-2 rounded-lg transition-colors ${num <= formData.rating ? 'text-amber-400' : 'text-gray-600 hover:text-amber-400'} hover:bg-amber-400/10`}
                    aria-label={`Рейтинг ${num}`}
                  >
                    <Star className={`w-5 h-5 ${num <= formData.rating ? 'fill-amber-400/90' : ''}`} />
                  </button>
                ))}
                <span className="ml-2 text-xs text-gray-500">{formData.rating} / 5</span>
              </div>
            </div>
            {/* Category */}
            <div className="relative group">
              <select
                value={formData.category}
                onChange={e => setFormData({ ...formData, category: e.target.value as Account['category'] })}
                className="w-full h-11 pl-3 pr-8 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 appearance-none"
              >
                <option value="lead">Лид</option>
                <option value="client">Клиент</option>
                <option value="partner">Партнер</option>
                <option value="spam">Спам</option>
                <option value="other">Другое</option>
              </select>
              <span className="absolute -top-2 left-2 bg-surface-50/90 backdrop-blur px-1 text-[9px] font-medium text-gray-500 tracking-wide">Категория</span>
            </div>
            {/* Source */}
            <div className="relative group">
              <select
                value={formData.source}
                onChange={e => setFormData({ ...formData, source: e.target.value as Account['source'] })}
                className="w-full h-11 pl-3 pr-8 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 appearance-none"
              >
                <option value="private">Личные сообщения</option>
                <option value="group">Групповые чаты</option>
              </select>
              <span className="absolute -top-2 left-2 bg-surface-50/90 backdrop-blur px-1 text-[9px] font-medium text-gray-500 tracking-wide">Источник</span>
            </div>
            {/* Account ID (display only) */}
            {editingAccount && (
              <div className="sm:col-span-2 flex flex-col gap-1 text-[10px] text-gray-500 bg-surface-100/50 border border-dashed border-white/10 rounded-xl p-3">
                <div className="flex flex-wrap gap-x-6 gap-y-1">
                  <span><span className="font-medium text-gray-600">ID аккаунта:</span> {editingAccount.id}</span>
                  <span><span className="font-medium text-gray-600">User ID:</span> {editingAccount.user_id}</span>
                  {editingAccount.created_at && (
                    <span><span className="font-medium text-gray-600">Создан в CRM:</span> {new Date(editingAccount.created_at).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
            )}
            {/* Registration Date */}
            <div>
              <label className="text-[10px] font-medium text-gray-400 mb-1">Дата регистрации аккаунта</label>
              <input
                type="date"
                value={formData.registration_date}
                onChange={e => setFormData({ ...formData, registration_date: e.target.value })}
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all"
                max={new Date().toISOString().slice(0,10)}
              />
            </div>
            {/* Brand Name */}
            <div>
              <label className="text-[10px] font-medium text-gray-400 mb-1">Имя бренда / Компания</label>
              <input
                type="text"
                value={formData.brand_name}
                onChange={e => setFormData({ ...formData, brand_name: e.target.value })}
                placeholder="Напр. Acme Corp"
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all placeholder:text-gray-500"
              />
            </div>
            {/* Position */}
            <div>
              <label className="text-[10px] font-medium text-gray-400 mb-1">Должность</label>
              <input
                type="text"
                value={formData.position}
                onChange={e => setFormData({ ...formData, position: e.target.value })}
                placeholder="CEO, Маркетолог..."
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all placeholder:text-gray-500"
              />
            </div>
            {/* Years in Market */}
            <div>
              <label className="text-[10px] font-medium text-gray-400 mb-1">Сколько лет на рынке</label>
              <input
                type="number"
                min={0}
                max={150}
                inputMode="numeric"
                value={formData.years_in_market}
                onChange={e => setFormData({ ...formData, years_in_market: e.target.value.replace(/[^0-9]/g,'') })}
                placeholder="Напр. 5"
                className="w-full h-11 px-3 rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all"
              />
            </div>
          </div>
          {/* Tags */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-medium text-gray-400 flex items-center gap-1"><Hash className="w-3 h-3" />Теги</span>
              <span className="text-[10px] text-gray-400">Enter / запятая для добавления</span>
            </div>
            <div className="flex flex-wrap gap-2 rounded-xl border border-white/10 bg-surface-100/60 px-3 py-2 focus-within:ring-2 focus-within:ring-blue-500/40 focus-within:border-blue-500/60 transition-all">
              {tags.map(t => (
                <span key={t} className="group/tag inline-flex items-center gap-1 text-[10px] bg-gradient-to-r from-blue-600/40 to-indigo-600/40 text-blue-200 px-2 py-1 rounded-full border border-blue-400/30">
                  {t}
                  <button type="button" onClick={() => removeTag(t)} className="opacity-60 group-hover/tag:opacity-100 hover:text-red-500">
                    ×
                  </button>
                </span>
              ))}
              <input
                value={tagInput}
                onChange={e => setTagInput(e.target.value)}
                onBlur={() => commitTag()}
                onKeyDown={e => {
                  if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); commitTag(); }
                  if (e.key === 'Backspace' && !tagInput && tags.length) removeTag(tags[tags.length-1]);
                }}
                placeholder={tags.length ? '' : 'важный, vip...'}
                className="flex-1 min-w-[80px] bg-transparent outline-none text-[10px] text-gray-300 placeholder:text-gray-500"
              />
            </div>
          </div>
          {/* Notes */}
          <div>
            <label className="text-[10px] font-medium text-gray-400 mb-1 flex items-center gap-1"><FileText className="w-3.5 h-3.5 text-gray-500" />Заметки</label>
            <textarea
              value={formData.notes}
              onChange={e => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Дополнительная информация..."
              rows={3}
              className="w-full rounded-xl border border-white/10 bg-surface-100/60 focus:bg-surface-100/80 text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/60 transition-all resize-none px-3 py-2 placeholder:text-gray-500"
            />
          </div>
          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-2">
            <button
              type="submit"
              className="flex-1 inline-flex items-center justify-center h-11 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white text-sm font-medium shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-blue-500/60 focus:ring-offset-0 transition-all"
            >
              {isEdit ? 'Сохранить изменения' : 'Создать аккаунт'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 inline-flex items-center justify-center h-11 rounded-xl border border-white/10 bg-surface-100/60 text-sm font-medium text-gray-300 hover:bg-surface-100/80 focus:outline-none focus:ring-2 focus:ring-white/20 focus:ring-offset-0 transition-all"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AccountModal;