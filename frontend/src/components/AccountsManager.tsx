import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { 
  Plus, 
  Search, 
  Star, 
  Edit3, 
  Trash2, 
  User
} from 'lucide-react';
import { Account } from '../types';
import AccountModal from './AccountModal';

const AccountsManager: React.FC = () => {
  const { accounts, addAccount, updateAccount, deleteAccount } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterSource, setFilterSource] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'last_contact'>('name');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);

  // Form state moved to AccountModal

  const categories = [
    { value: 'all', label: 'Все' },
    { value: 'client', label: 'Клиенты' },
    { value: 'partner', label: 'Партнеры' },
    { value: 'lead', label: 'Лиды' },
    { value: 'spam', label: 'Спам' },
    { value: 'other', label: 'Другое' }
  ];

  const sources = [
    { value: 'all', label: 'Все источники' },
    { value: 'private', label: 'Личные сообщения' },
    { value: 'group', label: 'Групповые чаты' }
  ];

  const filteredAndSortedAccounts = accounts
    .filter(account => {
      const term = searchTerm.toLowerCase();
      const matchesSearch = 
        (account.first_name || '').toLowerCase().includes(term) ||
        (account.last_name || '').toLowerCase().includes(term) ||
        (account.username || '').toLowerCase().includes(term);
      
      const matchesCategory = filterCategory === 'all' || account.category === filterCategory;
      const matchesSource = filterSource === 'all' || account.source === filterSource;
      
      return matchesSearch && matchesCategory && matchesSource;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return (a.first_name || '').localeCompare(b.first_name || '');
        case 'rating':
          return b.rating - a.rating;
        case 'last_contact':
          return new Date(b.last_contact).getTime() - new Date(a.last_contact).getTime();
        default:
          return 0;
      }
    });

  const resetForm = () => {
    setEditingAccount(null);
    setIsModalOpen(false);
  };

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setIsModalOpen(true);
  };

  const getCategoryColor = (category: Account['category']) => {
    // High-contrast pill styles (solid-ish backgrounds, readable text)
    const colors: Record<Account['category'], string> = {
      client: 'bg-green-600 text-white',
      partner: 'bg-blue-600 text-white',
      // Yellow needs dark text for accessibility
      lead: 'bg-yellow-400 text-gray-900',
      spam: 'bg-red-600 text-white',
      other: 'bg-gray-600 text-white'
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

  const getSourceColor = (source: Account['source']) => {
    const colors: Record<Account['source'], string> = {
      private: 'bg-indigo-600 text-white',
      group: 'bg-purple-600 text-white'
    };
    return colors[source];
  };

  const getSourceLabel = (source: Account['source']) => {
    const labels = {
      private: 'ЛС',
      group: 'Группа'
    };
    return labels[source];
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
  <div className="flex-1 flex flex-col bg-surface-0 text-gray-200 overflow-hidden">
      {/* Header */}
  <div className="bg-surface-50/70 backdrop-blur-md border-b border-white/5 p-4 lg:p-6 shadow-elevated-sm">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl lg:text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-cyan-200 to-purple-300">Управление аккаунтами</h1>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-3 lg:px-4 py-2 rounded-lg flex items-center space-x-2 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white text-sm shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Добавить аккаунт</span>
          </button>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1 min-w-0">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input
              type="text"
              placeholder="Поиск по имени или username..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 transition-colors placeholder:text-gray-500 text-sm"
            />
          </div>

          <div className="flex gap-2 lg:gap-4">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="flex-1 lg:flex-none px-3 lg:px-4 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-sm"
            >
              {categories.map(category => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>

            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value)}
              className="flex-1 lg:flex-none px-3 lg:px-4 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-sm"
            >
              {sources.map(source => (
                <option key={source.value} value={source.value}>
                  {source.label}
                </option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="flex-1 lg:flex-none px-3 lg:px-4 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-sm"
            >
              <option value="name">По имени</option>
              <option value="rating">По рейтингу</option>
              <option value="last_contact">По дате контакта</option>
            </select>
          </div>
        </div>
      </div>

      {/* Accounts List */}
  <div className="flex-1 overflow-y-auto p-4 lg:p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
          {filteredAndSortedAccounts.map(account => (
            <div key={account.id} className="rounded-lg p-4 lg:p-6 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm hover:shadow-elevated transition-shadow">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 lg:w-12 lg:h-12 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-inner-glow">
                    <span className="text-white font-semibold text-sm lg:text-lg">
                      {(account.first_name || account.username || '?').charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-gray-100 truncate text-sm">
                      {(() => {
                        const full = [account.first_name, account.last_name].filter(Boolean).join(' ').trim();
                        if (full) return full;
                        if (account.username) return '@' + account.username;
                        return 'Без имени';
                      })()}
                    </h3>
                    {account.username && (account.first_name || account.last_name) && (
                      <p className="text-[10px] text-gray-500 truncate">@{account.username}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleEdit(account)}
                    className="p-1 text-gray-500 hover:text-blue-300 hover:bg-white/5 rounded-md transition-colors"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteAccount(account.id)}
                    className="p-1 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Rating */}
              <div className="flex items-center space-x-2 mb-3">
                <div className="flex">
                  {renderStars(account.rating)}
                </div>
                <span className="text-[10px] text-gray-500">({account.rating}/5)</span>
              </div>

              {/* Category and Tags */}
              <div className="flex flex-wrap gap-2 mb-3">
                <span className={`px-2 py-1 rounded-full text-[10px] font-medium shadow-sm ring-1 ring-white/10 ${getCategoryColor(account.category)}`}> 
                  {getCategoryLabel(account.category)}
                </span>
                <span className={`px-2 py-1 rounded-full text-[10px] font-medium shadow-sm ring-1 ring-white/10 ${getSourceColor(account.source)}`}>
                  {getSourceLabel(account.source)}
                </span>
                {account.tags.map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-1 rounded-full text-[10px] font-medium bg-gray-700 text-gray-100 shadow-sm ring-1 ring-white/5"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Notes */}
              {account.notes && (
                <p className="text-xs text-gray-400 mb-3 line-clamp-2">
                  {account.notes}
                </p>
              )}

              {/* Stats */}
              <div className="text-[10px] text-gray-500 space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-400">Сообщений:</span>
                  <span>{account.total_messages}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Последний контакт:</span>
                  <span>
                    {new Date(account.last_contact).toLocaleDateString('ru-RU')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredAndSortedAccounts.length === 0 && (
          <div className="text-center py-12">
            <User className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-300 mb-2">
              Аккаунты не найдены
            </h3>
            <p className="text-gray-500 mb-4">
              Попробуйте изменить параметры поиска или добавить новый аккаунт
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-2 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white text-sm shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 transition-all"
            >
              Добавить аккаунт
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      <AccountModal
        isOpen={isModalOpen}
        onClose={resetForm}
        editingAccount={editingAccount}
        onCreate={addAccount}
        onUpdate={updateAccount}
      />
    </div>
  );
};

export default AccountsManager;