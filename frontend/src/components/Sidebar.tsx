import React from 'react';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import {
  MessageCircle,
  Users,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bot,
  Link2,
  RefreshCw
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const { currentView, setCurrentView, sidebarCollapsed, setSidebarCollapsed, sidebarOpen, setSidebarOpen, balance, isLoadingBalance, loadBalance } = useAppContext();
  const { logout } = useAuth();

  const navItems = [
    { id: 'chats' as const, icon: MessageCircle, label: 'Чаты' },
  { id: 'botchats' as const, icon: Bot, label: 'Админ Чаты' },
    { id: 'accounts' as const, icon: Users, label: 'Аккаунты' },
    { id: 'transfers' as const, icon: Link2, label: 'Передачи' },
    { id: 'analytics' as const, icon: BarChart3, label: 'Аналитика' },
    { id: 'settings' as const, icon: Settings, label: 'Настройки' },
  ];

  return (
  <div className={`transition-all duration-300 flex flex-col lg:relative fixed z-40 h-full lg:h-auto bg-surface-50/70 backdrop-blur-md border-r border-white/5 shadow-elevated
    ${sidebarCollapsed ? 'lg:w-16' : 'lg:w-64'}
    w-64
    ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}` }>
      {/* Header */}
  <div className="p-4 border-b border-white/5 flex items-center justify-between relative">
        {/* Mobile close button when open */}
        {sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden absolute right-2 top-2 p-2 rounded-md bg-surface-100/70 backdrop-blur-md border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 shadow"
            aria-label="Закрыть меню"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        )}
        {!sidebarCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="relative">
              <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 opacity-25 blur" />
              <Bot className="w-8 h-8 relative text-blue-300 drop-shadow" />
            </div>
            <h1 className="text-xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-cyan-200 to-purple-300">Telegram CRM</h1>
          </div>
        )}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="p-1 rounded-md transition-colors text-gray-400 hover:text-white hover:bg-white/5"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2">
        <ul className="space-y-2">
          {navItems.map(item => (
            <li key={item.id}>
              <button
                onClick={() => setCurrentView(item.id)}
                className={`group w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 relative overflow-hidden ${
                  currentView === item.id
                    ? 'bg-gradient-to-r from-blue-600/80 via-indigo-600/70 to-purple-600/70 text-white shadow-glow-blue shadow-elevated-sm'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-white/5'
                }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0 drop-shadow-sm" />
                {!sidebarCollapsed && (
                  <span className="font-medium tracking-wide text-sm">{item.label}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/5 space-y-3">
        {!sidebarCollapsed && (
          <>
            {/* Balance Info */}
            <div className="flex items-center justify-between text-xs text-gray-400 bg-surface-100/30 rounded-lg p-2">
              <div className="flex items-center space-x-2">
                <Bot className="w-3 h-3" />
                <span className="tracking-wide">Баланс:</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="font-medium text-green-300">
                  {balance ? balance.formatted_balance : '$0.00'}
                </span>
                <button
                  onClick={loadBalance}
                  disabled={isLoadingBalance}
                  className="p-1 rounded-md hover:bg-white/10 transition-colors disabled:opacity-50"
                  title="Обновить баланс"
                >
                  <RefreshCw className={`w-3 h-3 ${isLoadingBalance ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              <div className="relative">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                <div className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-40" />
              </div>
              <span className="tracking-wide">Подключено к Telegram</span>
            </div>
          </>
        )}

        {/* Balance button for collapsed sidebar */}
        {sidebarCollapsed && (
          <button
            onClick={loadBalance}
            disabled={isLoadingBalance}
            className="w-full flex justify-center p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors disabled:opacity-50"
            title="Обновить баланс"
          >
            <RefreshCw className={`w-4 h-4 ${isLoadingBalance ? 'animate-spin' : ''}`} />
          </button>
        )}

        <button
          onClick={logout}
          className="w-full text-xs font-medium tracking-wide rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 py-2 transition"
        >
          {sidebarCollapsed ? '↩' : 'Выйти'}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;