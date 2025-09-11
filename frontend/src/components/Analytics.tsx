import React from 'react';
import { useAppContext } from '../context/AppContext';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  MessageCircle, 
  Star,
  Calendar,
  Target,
  Award
} from 'lucide-react';

const Analytics: React.FC = () => {
  const { analyticsData, accounts } = useAppContext();

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    change?: string;
    icon: React.ElementType;
  }> = ({ title, value, change, icon: Icon }) => (
  <div className="rounded-lg p-6 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wide">{title}</p>
          <p className="text-xl font-semibold text-gray-100 mt-1">{value}</p>
          {change && (
            <p className="text-[11px] text-emerald-400 flex items-center mt-1">
              <TrendingUp className="w-4 h-4 mr-1" />
              {change}
            </p>
          )}
        </div>
        <div className="p-3 rounded-lg bg-gradient-to-br from-surface-200/60 to-surface-200/20 border border-white/5 shadow-inner-glow">
          <Icon className="w-5 h-5 text-cyan-300" />
        </div>
      </div>
    </div>
  );

  const getAverageRating = () => {
    if (accounts.length === 0) return 0;
    const total = accounts.reduce((sum, account) => sum + account.rating, 0);
    return (total / accounts.length).toFixed(1);
  };

  const getCategoryStats = () => {
    const stats = accounts.reduce((acc, account) => {
      acc[account.category] = (acc[account.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(stats)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);
  };

  const getTopRatedAccounts = () => {
    return accounts
      .filter(account => account.rating >= 4)
      .sort((a, b) => b.rating - a.rating)
      .slice(0, 5);
  };

  const categoryLabels: Record<string, string> = {
    client: 'Клиенты',
    partner: 'Партнеры',
    lead: 'Лиды',
    spam: 'Спам',
    other: 'Другое'
  };

  const categoryColors: Record<string, string> = {
    client: 'bg-green-500',
    partner: 'bg-blue-500',
    lead: 'bg-yellow-500',
    spam: 'bg-red-500',
    other: 'bg-gray-500'
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
  <div className="flex-1 bg-surface-0 text-gray-200 overflow-y-auto">
      <div className="p-4 lg:p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-xl lg:text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-cyan-200 to-purple-300 mb-2">Аналитика</h1>
          <p className="text-gray-500 text-sm">Подробная статистика вашей работы с клиентами</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
          <StatCard title="Диалогов сегодня" value={analyticsData.daily_chats} change="+8.2%" icon={MessageCircle} />
          <StatCard title="Новых контактов" value={analyticsData.new_contacts} change="+12%" icon={Users} />
          <StatCard title="Всего сообщений" value={analyticsData.total_messages} change="+5.1%" icon={BarChart3} />
          <StatCard title="Средний рейтинг" value={getAverageRating()} icon={Star} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          {/* Activity Chart */}
          <div className="rounded-lg p-4 lg:p-6 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm">
            <h2 className="text-sm font-semibold text-gray-100 mb-4 flex items-center tracking-wide">
              <Calendar className="w-4 h-4 mr-2 text-blue-400" />
              Активность за неделю
            </h2>
            <div className="space-y-4">
              {analyticsData.activity_chart.map((day) => (
                <div key={day.date} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-[11px] text-gray-500 w-20">
                      {new Date(day.date).toLocaleDateString('ru-RU', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </span>
                    <div className="flex-1">
                      <div className="bg-surface-200/40 rounded-full h-2 w-32">
                        <div 
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full shadow-glow-blue" 
                          style={{ width: `${(day.messages / 150) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div className="text-[11px] text-gray-200 font-medium">
                    {day.messages} сообщений
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Categories Distribution */}
          <div className="rounded-lg p-6 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm">
            <h2 className="text-sm font-semibold text-gray-100 mb-4 flex items-center tracking-wide">
              <Target className="w-4 h-4 mr-2 text-purple-400" />
              Распределение по категориям
            </h2>
            <div className="space-y-4">
              {getCategoryStats().map(({ category, count }) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2.5 h-2.5 rounded-full ${categoryColors[category]}`}></div>
                    <span className="text-[11px] text-gray-400">
                      {categoryLabels[category] || category}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="bg-surface-200/40 rounded-full h-2 w-20">
                      <div 
                        className={`h-2 rounded-full ${categoryColors[category]}`}
                        style={{ width: `${(count / accounts.length) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-[11px] font-medium text-gray-200 w-8 text-right">
                      {count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Rated Accounts */}
          <div className="rounded-lg p-6 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm">
            <h2 className="text-sm font-semibold text-gray-100 mb-4 flex items-center tracking-wide">
              <Award className="w-4 h-4 mr-2 text-amber-400" />
              Топ аккаунты по рейтингу
            </h2>
            <div className="space-y-4">
              {getTopRatedAccounts().map((account, index) => (
                <div key={account.id} className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <span className={`
                      inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium
                      ${index === 0 ? 'bg-yellow-100 text-yellow-800' : 
                        index === 1 ? 'bg-gray-100 text-gray-800' :
                        index === 2 ? 'bg-orange-100 text-orange-800' :
                        'bg-blue-100 text-blue-800'}
                    `}>
                      {index + 1}
                    </span>
                  </div>
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-inner-glow">
                    <span className="text-white font-semibold text-xs">
                      {account.first_name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-100 truncate">
                      {account.first_name} {account.last_name}
                    </p>
                    <div className="flex items-center space-x-1">
                      {renderStars(account.rating)}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-[10px] font-medium ${
                    account.category === 'client' ? 'bg-green-600/30 text-green-300 border border-green-500/30' :
                    account.category === 'partner' ? 'bg-blue-600/30 text-blue-300 border border-blue-500/30' :
                    'bg-yellow-600/30 text-yellow-300 border border-yellow-500/30'
                  }`}>
                    {categoryLabels[account.category]}
                  </span>
                </div>
              ))}
              
              {getTopRatedAccounts().length === 0 && (
                <p className="text-gray-500 text-xs text-center py-4">
                  Нет аккаунтов с высоким рейтингом
                </p>
              )}
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="rounded-lg p-6 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm">
            <h2 className="text-sm font-semibold text-gray-100 mb-4 flex items-center tracking-wide">
              <TrendingUp className="w-4 h-4 mr-2 text-emerald-400" />
              Показатели эффективности
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-surface-200/40 rounded-lg border border-white/5">
                <span className="text-[11px] text-gray-400">Конверсия лид → клиент</span>
                <span className="text-[11px] font-semibold text-emerald-400">23.5%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-200/40 rounded-lg border border-white/5">
                <span className="text-[11px] text-gray-400">Среднее время ответа</span>
                <span className="text-[11px] font-semibold text-blue-400">12 мин</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-200/40 rounded-lg border border-white/5">
                <span className="text-[11px] text-gray-400">Активных диалогов</span>
                <span className="text-[11px] font-semibold text-purple-400">8</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-200/40 rounded-lg border border-white/5">
                <span className="text-[11px] text-gray-400">Удовлетворенность</span>
                <span className="text-[11px] font-semibold text-amber-300">4.7/5</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;