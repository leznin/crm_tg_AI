import React, { useEffect, useRef, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import ChatMessages from './ChatMessages';
import ChatSummaryPanel from './ChatSummaryPanel';
import { Send, ArrowLeft, Info, User } from 'lucide-react';
import AccountModal from './AccountModal';

const ChatWindow: React.FC = () => {
	const { activeChat, sendMessage, sidebarCollapsed, setSidebarCollapsed, chats, setActiveChat, activeManager, accounts, addAccount, updateAccount, setSidebarOpen } = useAppContext();
	const [accountModalOpen, setAccountModalOpen] = useState(false);
	const existingAccount = activeChat ? accounts.find(a => a.user_id === activeChat.id) : null;
	const [messageText, setMessageText] = useState('');
	const inputRef = useRef<HTMLTextAreaElement | null>(null);

	useEffect(() => { if (activeChat && inputRef.current) inputRef.current.focus(); }, [activeChat]);

	const handleSend = () => {
		if (!activeChat || !messageText.trim()) return;
		sendMessage(activeChat.id, messageText.trim());
		setMessageText('');
	};

	const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
		if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
	};

	const getChatTitle = () => {
		if (!activeChat) return '';
		const name = [activeChat.first_name, activeChat.last_name].filter(Boolean).join(' ').trim();
		return activeChat.title || name || (activeChat.username ? '@' + activeChat.username : 'Без названия');
	};

	if (!activeManager) {
		return (
			<div className="flex-1 flex flex-col items-center justify-center bg-surface-50/40 backdrop-blur-md">
				<div className="max-w-md text-center px-6">
					<div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">M</div>
					<h2 className="text-2xl font-bold text-gray-900 mb-3">Выберите менеджера</h2>
					<p className="text-gray-600 mb-6">Чтобы начать работу, выберите менеджера слева. Его рабочие чаты появятся здесь.</p>
				</div>
			</div>
		);
	}

	if (!activeChat) {
		return (
			<div className="flex-1 flex flex-col items-center justify-center bg-surface-50/40 backdrop-blur-md">
				<div className="max-w-md text-center px-6">
					<div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">T</div>
					<h2 className="text-2xl font-bold text-gray-900 mb-3">Выберите диалог</h2>
					<p className="text-gray-600 mb-6">Чтобы начать работу, выберите чат из списка слева. Здесь будет отображаться история сообщений.</p>
					{chats.length === 0 && (<p className="text-sm text-gray-500">Пока нет чатов.</p>)}
				</div>
			</div>
		);
	}

	return (
		<>
		<div className="flex-1 flex flex-col bg-surface-50/60 backdrop-blur-md overflow-hidden border-l border-white/5">
			<div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-surface-100/60 backdrop-blur-sm">
				<div className="flex items-center space-x-3 min-w-0">
					<button
						className="lg:hidden p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5"
						onClick={() => { setSidebarOpen(true); setActiveChat(null); }}
						aria-label="Назад к списку чатов"
					>
						<ArrowLeft className="w-5 h-5" />
					</button>
					<div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-inner-glow">
						<span className="text-white font-semibold text-sm">{getChatTitle().charAt(0).toUpperCase()}</span>
					</div>
					<div className="min-w-0">
						<h2 className="font-semibold text-gray-100 truncate max-w-xs md:max-w-md text-sm tracking-wide">{getChatTitle()}</h2>
						{activeChat?.username && (<p className="text-[10px] text-gray-500 truncate">@{activeChat.username}</p>)}
					</div>
				</div>
				<div className="flex items-center space-x-2">
					<button
						className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5"
						onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
						aria-label="Переключить боковую панель"
					>
						<Info className="w-5 h-5" />
					</button>
					<button
						className="relative p-2 rounded-lg text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-blue-500/60 transition-colors"
						onClick={() => setAccountModalOpen(true)}
						aria-label="Карточка клиента"
					>
						<User className="w-5 h-5" />
						<span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_0_2px_rgba(0,0,0,0.5)] animate-pulse" />
					</button>
				</div>
			</div>
			<div className="flex flex-1 overflow-hidden">
				<div className="flex-1 overflow-y-auto">
					<ChatMessages />
				</div>
				<ChatSummaryPanel />
			</div>
			<div className="border-t border-white/5 p-4 bg-surface-100/40 backdrop-blur-md">
				<div className="flex items-end space-x-3">
					<div className="flex-1 relative">
						<textarea
							ref={inputRef}
							value={messageText}
							onChange={(e) => setMessageText(e.target.value)}
							onKeyDown={handleKeyDown}
							placeholder="Введите сообщение..."
							rows={1}
							className="w-full resize-none pr-12 p-3 rounded-lg bg-surface-200/40 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 transition-colors text-sm placeholder:text-gray-500 text-gray-200"
						/>
						<div className="absolute right-3 bottom-3 flex items-center space-x-2">
							<span className="text-[10px] text-gray-500 tracking-wide">Enter — отправить</span>
						</div>
					</div>
					<button
						onClick={handleSend}
						disabled={!messageText.trim()}
						className="h-11 px-5 rounded-lg flex items-center space-x-2 font-medium bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-sm shadow-glow-blue"
					>
						<Send className="w-4 h-4" />
						<span className="hidden sm:inline">Отправить</span>
					</button>
				</div>
			</div>
		</div>
		<AccountModal
			isOpen={accountModalOpen}
			onClose={() => setAccountModalOpen(false)}
			editingAccount={existingAccount || undefined}
			onCreate={async (data) => { 
				try {
					await addAccount({ ...data, manager_id: data.manager_id }); 
					setAccountModalOpen(false); 
				} catch (error) {
					console.error('Error creating account:', error);
					alert('Ошибка при создании контакта. Проверьте консоль для деталей.');
				}
			}}
			onUpdate={async (id, updates) => { 
				try {
					await updateAccount(id, updates); 
					setAccountModalOpen(false); 
				} catch (error) {
					console.error('Error updating account:', error);
					alert('Ошибка при обновлении контакта. Проверьте консоль для деталей.');
				}
			}}
			initialChat={!existingAccount ? activeChat || undefined : undefined}
		/>
		</>
	);
};

export default ChatWindow;