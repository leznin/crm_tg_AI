import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Bot, MessageSquare, Lightbulb, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';

const ChatSummaryPanel: React.FC = () => {
  const { activeChat, getChatSummary } = useAppContext();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [summary, setSummary] = useState<any>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);

  if (!activeChat) return null;

  const handleGetSummary = async () => {
    if (!activeChat) return;

    setIsLoadingSummary(true);
    try {
      // For regular chats, we need to check if this is a business chat or regular chat
      // For now, assume it's a business chat since regular chats might not have the same API
      const response = await fetch(`/api/v1/business-accounts/chats/${activeChat.id}/summary`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const summaryData = await response.json();
      setSummary(summaryData);
    } catch (error) {
      console.error('Error getting summary:', error);
      // Show error message to user
      alert('Ошибка при получении резюме. Проверьте настройки OpenRouter API.');
    } finally {
      setIsLoadingSummary(false);
    }
  };

  const suggestedReplies = [
    'Да, конечно! Давайте встретимся в пятницу в 14:00.',
    'Отправлю вам детальное предложение до конца дня.',
    'Хорошо, учту все ваши пожелания в проекте.',
    'Спасибо за обратную связь! Внесу правки.'
  ];

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      default: return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getSentimentText = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'Позитивный';
      case 'negative': return 'Негативный';
      default: return 'Нейтральный';
    }
  };

  return (
    <div className={`bg-surface-50/70 backdrop-blur-md border-l border-white/5 transition-all duration-300 ${isCollapsed ? 'w-12' : 'w-80'} flex-shrink-0 hidden lg:flex lg:flex-col shadow-elevated-sm`}>
      {/* Collapse button */}
      <div className="border-b border-white/5 p-2">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-center p-2 hover:bg-white/5 rounded-md transition-colors text-gray-400 hover:text-gray-200"
        >
          {isCollapsed ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5 text-cyan-400" />
              <span className="font-medium text-gray-200 text-sm">AI Помощник</span>
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </div>
          )}
        </button>
      </div>

      {!isCollapsed && (
        <div className="flex flex-col h-full">
          {/* Added extra bottom padding (pb-28) so content isn't hidden behind the chat composer */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-28 text-gray-200">
            {/* Chat Summary */}
            <div className="rounded-lg p-4 bg-gradient-to-br from-surface-100/60 to-surface-200/60 border border-white/5 shadow-elevated-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="w-5 h-5 text-blue-400" />
                  <h3 className="font-medium text-gray-100 text-sm">Резюме диалога</h3>
                </div>
                {!summary && (
                  <button
                    onClick={handleGetSummary}
                    disabled={isLoadingSummary}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white text-xs rounded-md transition-colors flex items-center space-x-1"
                  >
                    {isLoadingSummary ? (
                      <>
                        <div className="animate-spin rounded-full h-3 w-3 border border-white border-t-transparent"></div>
                        <span>Загрузка...</span>
                      </>
                    ) : (
                      <span>Получить резюме</span>
                    )}
                  </button>
                )}
              </div>

              {summary ? (
                <>
                  <p className="text-xs text-gray-300 mb-3 leading-relaxed">
                    {summary.summary}
                  </p>

                  <div className="space-y-2">
                    <h4 className="text-[10px] font-medium text-gray-400 uppercase tracking-wide">
                      Ключевые моменты:
                    </h4>
                    <ul className="space-y-1">
                      {summary.key_points.map((point: string, index: number) => (
                        <li key={index} className="text-[11px] text-gray-300 flex items-start">
                          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-3 pt-3 border-t border-white/5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-gray-400">Настроение:</span>
                      <span className={`text-[10px] px-2 py-1 rounded-full ${getSentimentColor(summary.sentiment)}`}>
                        {getSentimentText(summary.sentiment)}
                      </span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-6">
                  <MessageSquare className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                  <p className="text-xs text-gray-500">
                    Резюме диалога еще не создано
                  </p>
                  <p className="text-[10px] text-gray-600 mt-1">
                    Нажмите кнопку "Получить резюме" для анализа
                  </p>
                </div>
              )}
            </div>

            {/* AI Question */}
            <div className="rounded-lg p-4 bg-surface-100/60 border border-white/5">
              <div className="flex items-center space-x-2 mb-3">
                <Lightbulb className="w-5 h-5 text-yellow-600" />
                <h3 className="font-medium text-gray-700">Вопрос AI</h3>
              </div>
              
              <textarea
                value={aiQuestion}
                onChange={(e) => setAiQuestion(e.target.value)}
                placeholder="Задайте вопрос по контексту диалога..."
                className="w-full p-3 text-xs rounded-md resize-none bg-surface-200/40 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-gray-200 placeholder:text-gray-500 transition-colors"
                rows={3}
              />
              
              <button className="mt-2 w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2 px-4 rounded-md text-xs font-medium hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 transition-all shadow-glow-blue">
                Получить ответ
              </button>
            </div>

            {/* Suggested Replies */}
            <div className="rounded-lg p-4 bg-gradient-to-br from-emerald-600/20 via-emerald-500/10 to-teal-500/10 border border-emerald-500/20">
              <div className="flex items-center space-x-2 mb-3">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <h3 className="font-medium text-emerald-300 text-sm">Предложенные ответы</h3>
              </div>
              
              <div className="space-y-2">
                {suggestedReplies.map((reply, index) => (
                  <button
                    key={index}
                    className="w-full text-left p-2 bg-surface-100/40 border border-emerald-500/20 rounded-md text-xs hover:bg-emerald-500/10 hover:border-emerald-400/30 transition-all duration-200 text-gray-200"
                    onClick={() => {
                      // Here you would normally set this as the message text
                      console.log('Selected reply:', reply);
                    }}
                  >
                    {reply}
                  </button>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default ChatSummaryPanel;