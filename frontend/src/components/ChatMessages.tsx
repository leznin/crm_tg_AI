import React from 'react';
import { useAppContext } from '../context/AppContext';

const ChatMessages: React.FC = () => {
  const { activeChat, createAccountFromChat } = useAppContext();

  // Ensure account is created/updated only once per active chat change
  const processedRef = React.useRef<Set<number>>(new Set());
  React.useEffect(() => {
    if (activeChat && !processedRef.current.has(activeChat.id)) {
      createAccountFromChat(activeChat, activeChat.id);
      processedRef.current.add(activeChat.id);
    }
  }, [activeChat, createAccountFromChat]);

  // Mock messages for demonstration
  const mockMessages = [
    {
      id: 1,
      chat_id: activeChat?.id || 1,
      sender_id: activeChat?.id || 1,
      text: 'Привет! Как дела с проектом?',
      date: Date.now() - 7200000,
      from_me: false
    },
    {
      id: 2,
      chat_id: activeChat?.id || 1,
      sender_id: 0,
      text: 'Привет! Проект идет по плану, завтра должны закончить первую фазу.',
      date: Date.now() - 7100000,
      from_me: true
    },
    {
      id: 3,
      chat_id: activeChat?.id || 1,
      sender_id: activeChat?.id || 1,
      text: 'Отлично! А что насчет дополнительных функций, о которых мы говорили?',
      date: Date.now() - 7000000,
      from_me: false
    },
    {
      id: 4,
      chat_id: activeChat?.id || 1,
      sender_id: 0,
      text: 'По дополнительным функциям - давайте обсудим их подробнее на встрече. Могу подготовить презентацию с вариантами.',
      date: Date.now() - 6900000,
      from_me: true
    },
    {
      id: 5,
      chat_id: activeChat?.id || 1,
      sender_id: activeChat?.id || 1,
      text: 'Звучит здорово! Когда можем встретиться?',
      date: Date.now() - 6800000,
      from_me: false
    }
  ];

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера';
    } else {
      return date.toLocaleDateString('ru-RU', { 
        day: 'numeric', 
        month: 'long' 
      });
    }
  };

  // Group messages by date
  const groupedMessages = mockMessages.reduce((groups, message) => {
    const date = new Date(message.date).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
    return groups;
  }, {} as Record<string, typeof mockMessages>);

  return (
  <div className="p-4 space-y-4 text-gray-200">
      {Object.entries(groupedMessages).map(([date, messages]) => (
        <div key={date}>
          {/* Date separator */}
          <div className="flex items-center justify-center my-6">
            <div className="px-3 py-1 rounded-full text-[10px] tracking-wide bg-surface-200/60 border border-white/5 shadow-inner-glow text-gray-400 backdrop-blur-sm">
              {formatDate(messages[0].date)}
            </div>
          </div>

          {/* Messages for this date */}
          {messages.map((message, index) => {
            const isConsecutive = 
              index > 0 && 
              messages[index - 1].from_me === message.from_me &&
              message.date - messages[index - 1].date < 300000; // 5 minutes

            return (
              <div
                key={message.id}
                className={`flex ${message.from_me ? 'justify-end' : 'justify-start'} ${
                  isConsecutive ? 'mt-1' : 'mt-4'
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-xl shadow-elevated-sm border ${
                    message.from_me
                      ? 'bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 text-white border-white/10 rounded-br-none'
                      : 'bg-surface-200/60 text-gray-100 border-white/5 rounded-bl-none'
                  }`}
                >
                  <p className="text-xs leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  <p
                    className={`text-[10px] mt-1 ${
                      message.from_me ? 'text-indigo-200/80' : 'text-gray-500'
                    }`}
                  >
                    {formatTime(message.date)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default ChatMessages;