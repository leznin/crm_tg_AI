import React from 'react';
import { useAppContext } from '../context/AppContext';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';
import ChatList from './ChatList';
import ChatWindow from './ChatWindow';
import BusinessChatList from './BusinessChatList';
import BusinessChatWindow from './BusinessChatWindow';
import AccountsManager from './AccountsManager';
import Analytics from './Analytics';
import Settings from './Settings';
import TransfersManager from './TransfersManager';
import BotChatsAdmin from './BotChatsAdmin';

const Layout: React.FC = () => {
  const { currentView, sidebarCollapsed, sidebarOpen, setSidebarOpen } = useAppContext();

  const renderMainContent = () => {
    switch (currentView) {
      case 'chats':
        return <BusinessChatWindow />;
      case 'accounts':
        return <AccountsManager />;
      case 'analytics':
        return <Analytics />;
      case 'settings':
        return <Settings />;
      case 'transfers':
        return <TransfersManager />;
      case 'botchats':
        return <BotChatsAdmin />;
      default:
        return <BusinessChatWindow />;
    }
  };

  return (
    <div className="flex h-screen bg-surface-0 text-gray-200 relative">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/40 backdrop-blur-sm z-30"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
      {/* Hamburger button when sidebar closed */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-3 left-3 z-50 p-2 rounded-lg bg-surface-100/70 backdrop-blur-md border border-white/10 text-gray-300 hover:text-white hover:bg-white/10 shadow"
          aria-label="Открыть меню"
        >
          <Menu className="w-5 h-5" />
        </button>
      )}
      {/* Main Sidebar */}
      <Sidebar />
      
      {/* Chat List - only visible in chats view */}
      {currentView === 'chats' && (
  <div className={`transition-all duration-300 ${sidebarCollapsed ? 'w-80' : 'w-80'} bg-surface-50/80 backdrop-blur-md border-r border-white/5 flex-shrink-0 hidden lg:block shadow-elevated-sm` }>
          <BusinessChatList />
        </div>
      )}
      
      {/* Main Content */}
  <div className="flex-1 flex flex-col overflow-hidden">
        {renderMainContent()}
      </div>
    </div>
  );
};

export default Layout;