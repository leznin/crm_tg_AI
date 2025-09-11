import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { Chat, Account } from '../types';
import { X, Star, Save, User } from 'lucide-react';

interface ContactModalProps {
  chat: Chat;
  account?: Account;
  onClose: () => void;
}

const ContactModal: React.FC<ContactModalProps> = ({ chat, account, onClose }) => {
  const { addAccount, updateAccount, createAccountFromChat } = useAppContext();
  
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    // Default rating changed to 1 star
    rating: 1,
    category: 'lead' as Account['category'],
    source: 'private' as Account['source'],
    tags: '',
    notes: ''
  });

  useEffect(() => {
    if (account) {
      setFormData({
        first_name: account.first_name,
        last_name: account.last_name || '',
        username: account.username || '',
        rating: account.rating,
        category: account.category,
        source: account.source,
        tags: account.tags.join(', '),
        notes: account.notes
      });
    } else {
      // Initialize with chat data
      setFormData({
        first_name: chat.first_name || '',
        last_name: chat.last_name || '',
        username: chat.username || '',
        // Default rating changed to 1 star when initializing from chat
        rating: 1,
        category: chat.type === 'private' ? 'lead' : 'other',
        source: chat.type === 'private' ? 'private' : 'group',
        tags: '',
        notes: `Автоматически создан из ${chat.type === 'private' ? 'личного чата' : 'группового чата'}`
      });
    }
  }, [account, chat]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const accountData = {
      user_id: chat.id,
      first_name: formData.first_name,
      last_name: formData.last_name || undefined,
      username: formData.username || undefined,
      rating: formData.rating,
      category: formData.category,
      source: formData.source,
      tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
      notes: formData.notes,
      created_at: account?.created_at || new Date().toISOString(),
      last_contact: new Date().toISOString(),
      total_messages: account?.total_messages || 0,
      chat_type: chat.type
    };

    if (account) {
      updateAccount(account.id, accountData);
    } else {
      addAccount(accountData);
    }

    onClose();
  };

  const getCategoryColor = (category: Account['category']) => {
    const colors = {
      client: 'bg-green-100 text-green-800',
      partner: 'bg-blue-100 text-blue-800',
      lead: 'bg-yellow-100 text-yellow-800',
      spam: 'bg-red-100 text-red-800',
      other: 'bg-gray-100 text-gray-800'
    };
    return colors[category];
  };

  const getCategoryLabel = (category: Account['category']) => {
    const labels = {
      client: 'Клиент',
      partner: 'Партнер',
      lead: 'Лид',
      spam: 'Спам',
      other: 'Другое'
    };
    return labels[category];
  };

  const renderStars = (rating: number, interactive = false) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-5 h-5 ${interactive ? 'cursor-pointer' : ''} ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
        onClick={interactive ? () => setFormData({ ...formData, rating: i + 1 }) : undefined}
      />
    ));
  };

  const title = chat.title || `${chat.first_name || ''} ${chat.last_name || ''}`.trim();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-lg">
                {title.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {account ? 'Редактировать контакт' : 'Создать контакт'}
              </h2>
              <p className="text-sm text-gray-500">{title}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Имя *
              </label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Фамилия
              </label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="@username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Рейтинг
            </label>
            <div className="flex items-center space-x-1">
              {renderStars(formData.rating, true)}
              <span className="ml-2 text-sm text-gray-600">({formData.rating}/5)</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Категория
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value as Account['category'] })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="lead">Лид</option>
                <option value="client">Клиент</option>
                <option value="partner">Партнер</option>
                <option value="spam">Спам</option>
                <option value="other">Другое</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Источник
              </label>
              <select
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value as Account['source'] })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="private">Личные сообщения</option>
                <option value="group">Групповые чаты</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Теги (через запятую)
            </label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="важный, vip, постоянный"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Заметки
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              rows={3}
              placeholder="Дополнительная информация о контакте..."
            />
          </div>

          {/* Account Stats */}
          {account && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Статистика</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Сообщений:</span>
                  <span className="ml-2 font-medium">{account.total_messages}</span>
                </div>
                <div>
                  <span className="text-gray-500">Создан:</span>
                  <span className="ml-2 font-medium">
                    {new Date(account.created_at).toLocaleDateString('ru-RU')}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">Последний контакт:</span>
                  <span className="ml-2 font-medium">
                    {new Date(account.last_contact).toLocaleDateString('ru-RU')}
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="flex space-x-4 pt-4">
            <button
              type="submit"
              className="flex-1 bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>{account ? 'Обновить' : 'Создать'}</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-400 transition-colors"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContactModal;