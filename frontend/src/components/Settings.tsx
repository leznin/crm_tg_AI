import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useAppContext } from '../context/AppContext';
import {
  Key,
  Bot,
  Database,
  Save,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle,
  ListPlus,
  X,
  Brain,
  Loader2,
  RefreshCw,
  Search,
  Volume2,
  FileText,
  Image as ImageIcon,
  ArrowRight,
  Mic,
  MessageSquare
} from 'lucide-react';

// Функция для отображения входа/выхода модели на основе возможностей (мульти-варианты)
const getCapabilityTags = (capabilities: string[] = []) => {
  type Tag = { icon: React.ComponentType<any>, label: string };
  const capabilityToIO: Record<string, { inputs: Tag[]; outputs: Tag[] }> = {
    text: {
      inputs: [{ icon: FileText, label: 'Текст' }],
      outputs: [{ icon: MessageSquare, label: 'Текст' }]
    },
    vision: {
      inputs: [{ icon: ImageIcon, label: 'Изображение' }],
      outputs: [{ icon: MessageSquare, label: 'Текст' }]
    },
    image_generation: {
      inputs: [{ icon: FileText, label: 'Текст' }],
      outputs: [{ icon: ImageIcon, label: 'Изображение' }]
    },
    audio: {
      inputs: [{ icon: Mic, label: 'Аудио' }],
      outputs: [{ icon: MessageSquare, label: 'Текст' }]
    }
  };

  const inputMap = new Map<string, Tag>();
  const outputMap = new Map<string, Tag>();
  for (const cap of capabilities) {
    const mapping = capabilityToIO[cap];
    if (!mapping) continue;
    for (const t of mapping.inputs) inputMap.set(t.label, t);
    for (const t of mapping.outputs) outputMap.set(t.label, t);
  }

  return {
    inputs: Array.from(inputMap.values()),
    outputs: Array.from(outputMap.values())
  } as { inputs: Tag[]; outputs: Tag[] };
};

// Вспомогательный компонент массового импорта ключевых слов
const BulkKeywordImport: React.FC<{ keywords: string[]; setKeywords: (k: string[]) => void; }> = ({ keywords, setKeywords }) => {
  const [status, setStatus] = React.useState<string | null>(null);
  const [addedCount, setAddedCount] = React.useState<number>(0);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  const onFile = (file: File) => {
    setStatus(null);
    setAddedCount(0);
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const text = String(reader.result || '');
        // Разделители: запятая, точка с запятой, перевод строки, табы, пробелы, вертикальная черта
        const tokens = text
          .split(/[;,\n\r\t| ]+/)
          .map(t => t.trim())
          .filter(Boolean);
        if (!tokens.length) {
          setStatus('Файл не содержит слов.');
          return;
        }
        const existingLower = new Set(keywords.map(k => k.toLowerCase()));
        const toAdd: string[] = [];
        for (const raw of tokens) {
          const norm = raw.toLowerCase();
          if (existingLower.has(norm) || toAdd.some(a => a.toLowerCase() === norm)) continue; // игнор дубликатов
          toAdd.push(raw.trim());
        }
        if (toAdd.length) {
          setKeywords([...keywords, ...toAdd]);
          setAddedCount(toAdd.length);
          setStatus(`Добавлено: ${toAdd.length}. Игнорировано дубликатов: ${tokens.length - toAdd.length}`);
        } else {
          setStatus('Новых слов не найдено (все дубликаты).');
        }
      } catch (e) {
        setStatus('Ошибка чтения файла');
      }
    };
    reader.onerror = () => setStatus('Ошибка чтения файла');
    reader.readAsText(file);
  };

  return (
    <div className="mt-6 pt-5 border-t border-white/5">
      <h4 className="text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-3">Массовый импорт</h4>
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt"
          className="hidden"
          onChange={e => { const f = e.target.files?.[0]; if (f) { onFile(f); e.target.value=''; } }}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="px-4 py-2 rounded-lg bg-surface-200/40 hover:bg-surface-200/60 border border-white/5 text-xs text-gray-300 flex items-center gap-2"
        >
          <span>Загрузить .txt</span>
        </button>
        {addedCount > 0 && (
          <span className="text-[10px] px-2 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">+{addedCount}</span>
        )}
      </div>
      {status && <div className="mt-2 text-[11px] text-gray-400">{status}</div>}
      <p className="mt-3 text-[10px] text-gray-500 leading-relaxed">Каждое слово может быть в отдельной строке или разделено пробелом, запятой, точкой с запятой, табуляцией или вертикальной чертой. Дубликаты игнорируются автоматически.</p>
    </div>
  );
};

const Settings: React.FC = () => {
  const { apiConfig, updateApiConfig, keywords, setKeywords } = useAppContext();
  const [activeTab, setActiveTab] = useState<'api' | 'prompts' | 'keywords' | 'models'>('api');
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'success' | 'error' | null>(null);
  const [prompts, setPrompts] = useState({
    summary: 'Создай краткое резюме этого диалога, выделив ключевые моменты и общий тон беседы.',
    suggestions: 'Предложи 3-4 варианта ответов на основе контекста диалога.',
    analysis: 'Проанализируй настроение собеседника и дай рекомендации по дальнейшему общению.'
  });
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(false);
  const [isSavingPrompts, setIsSavingPrompts] = useState(false);
  
  // OpenRouter models state
  const [availableModels, setAvailableModels] = useState<{
    text: any[];
    image_vision: any[];
    image_generation: any[];
    audio: any[];
  }>({ text: [], image_vision: [], image_generation: [], audio: [] });
  const [selectedModels, setSelectedModels] = useState({
    text: '',
    image_vision: '',
    image_generation: '',
    audio: ''
  });
  const [balance, setBalance] = useState<{
    balance: number;
    usage: number;
    formatted_balance: string;
    formatted_usage: string;
  } | null>(null);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);

  // Цвета для capability chips (используются в IO-тегах ниже)

  const [formData, setFormData] = useState({
    telegram_bot_token: apiConfig.telegram_bot_token || '',
    openrouter_api_key: apiConfig.openrouter_api_key || ''
  });

  // Track which fields have been modified by the user
  const [changedFields, setChangedFields] = useState<{
    telegram_bot_token: boolean;
    openrouter_api_key: boolean;
  }>({
    telegram_bot_token: false,
    openrouter_api_key: false
  });

  const tabs = [
    { id: 'api' as const, label: 'API ключи', icon: Key },
    { id: 'models' as const, label: 'AI Модели', icon: Brain },
    { id: 'prompts' as const, label: 'Промпты', icon: Bot },
    { id: 'keywords' as const, label: 'Ключевые слова', icon: ListPlus }
  ];

  const [newKeyword, setNewKeyword] = useState('');

  // Sync formData with apiConfig changes
  useEffect(() => {
    setFormData({
      telegram_bot_token: apiConfig.telegram_bot_token || '',
      openrouter_api_key: apiConfig.openrouter_api_key || ''
    });
    // Reset changed fields when apiConfig changes (e.g., after successful save)
    setChangedFields({
      telegram_bot_token: false,
      openrouter_api_key: false
    });
  }, [apiConfig]);

  // Load prompts and models from API on component mount
  useEffect(() => {
    loadPrompts();
    loadUserModels();
  }, []);

  const loadPrompts = async () => {
    setIsLoadingPrompts(true);
    try {
      const response = await fetch('/api/v1/settings/prompts', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPrompts({
          summary: data.summary || 'Создай краткое резюме этого диалога, выделив ключевые моменты и общий тон беседы.',
          suggestions: data.suggestions || 'Предложи 3-4 варианта ответов на основе контекста диалога.',
          analysis: data.analysis || 'Проанализируй настроение собеседника и дай рекомендации по дальнейшему общению.'
        });
      }
    } catch (error) {
      console.error('Error loading prompts:', error);
    } finally {
      setIsLoadingPrompts(false);
    }
  };

  const savePrompts = async () => {
    setIsSavingPrompts(true);
    try {
      const response = await fetch('/api/v1/settings/prompts', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(prompts),
      });

      if (response.ok) {
        setConnectionStatus('success');
        setTimeout(() => setConnectionStatus(null), 3000);
      } else {
        throw new Error('Failed to save prompts');
      }
    } catch (error) {
      console.error('Error saving prompts:', error);
      setConnectionStatus('error');
      setTimeout(() => setConnectionStatus(null), 3000);
    } finally {
      setIsSavingPrompts(false);
    }
  };

  // OpenRouter models functions
  const loadAvailableModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await fetch('/api/v1/settings/openrouter/models', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data);
      } else {
        console.error('Failed to load available models');
      }
    } catch (error) {
      console.error('Error loading available models:', error);
    } finally {
      setIsLoadingModels(false);
    }
  };

  const loadUserModels = async () => {
    try {
      const response = await fetch('/api/v1/settings/models', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const userModels = {
          text: '',
          image_vision: '',
          image_generation: '',
          audio: ''
        };
        
        data.forEach((model: any) => {
          if (model.data_type === 'text') userModels.text = model.model_name;
          if (model.data_type === 'image_vision') userModels.image_vision = model.model_name;
          if (model.data_type === 'image_generation') userModels.image_generation = model.model_name;
          if (model.data_type === 'audio') userModels.audio = model.model_name;
        });
        
        setSelectedModels(userModels);
      }
    } catch (error) {
      console.error('Error loading user models:', error);
    }
  };

  const loadBalance = async () => {
    setIsLoadingBalance(true);
    try {
      const response = await fetch('/api/v1/settings/openrouter/balance', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setBalance(data);
      } else {
        console.error('Failed to load balance');
      }
    } catch (error) {
      console.error('Error loading balance:', error);
    } finally {
      setIsLoadingBalance(false);
    }
  };

  // Auto-load models and balance when Models tab opens (no local storage)
  useEffect(() => {
    if (activeTab === 'models') {
      const isEmpty =
        availableModels.text.length === 0 &&
        availableModels.image_vision.length === 0 &&
        availableModels.image_generation.length === 0 &&
        availableModels.audio.length === 0;
      if (isEmpty && !isLoadingModels) {
        loadAvailableModels();
      }
      if (!balance && !isLoadingBalance) {
        loadBalance();
      }
    }
  }, [activeTab]);

  const saveSelectedModel = async (dataType: 'text' | 'image_vision' | 'image_generation' | 'audio', modelName: string) => {
    try {
      const response = await fetch('/api/v1/settings/models', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data_type: dataType,
          model_name: modelName,
          model_configuration: {}
        }),
      });

      if (response.ok) {
        setConnectionStatus('success');
        setTimeout(() => setConnectionStatus(null), 3000);
      } else {
        throw new Error('Failed to save model');
      }
    } catch (error) {
      console.error('Error saving model:', error);
      setConnectionStatus('error');
      setTimeout(() => setConnectionStatus(null), 3000);
    }
  };
  const addKeyword = () => {
    const val = newKeyword.trim();
    if (!val) return;
    if (keywords.some(k => k.toLowerCase() === val.toLowerCase())) { setNewKeyword(''); return; }
    setKeywords([...keywords, val]);
    setNewKeyword('');
  };
  const removeKeyword = (k: string) => setKeywords(keywords.filter(w => w !== k));

  const toggleShowKey = (keyName: string) => {
    setShowKeys(prev => ({
      ...prev,
      [keyName]: !prev[keyName]
    }));
  };

  // Handle input changes and mark fields as changed
  const handleInputChange = (fieldName: 'telegram_bot_token' | 'openrouter_api_key', value: string) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
    setChangedFields(prev => ({
      ...prev,
      [fieldName]: true
    }));
  };

  const handleSaveApiConfig = async () => {
    try {
      // Only send fields that have been changed by the user
      const configToSave: Partial<typeof formData> = {};

      if (changedFields.telegram_bot_token) {
        configToSave.telegram_bot_token = formData.telegram_bot_token;
      }

      if (changedFields.openrouter_api_key) {
        configToSave.openrouter_api_key = formData.openrouter_api_key;
      }

      // Only save if at least one field has been changed
      if (Object.keys(configToSave).length === 0) {
        setConnectionStatus('success');
        setTimeout(() => setConnectionStatus(null), 3000);
        return;
      }

      await updateApiConfig(configToSave);
      setConnectionStatus('success');
      setTimeout(() => setConnectionStatus(null), 3000);
    } catch (error) {
      console.error('Error saving API config:', error);
      setConnectionStatus('error');
      setTimeout(() => setConnectionStatus(null), 3000);
    }
  };

  const testConnection = async () => {
    setIsTestingConnection(true);
    // Simulate API test
    setTimeout(() => {
      setConnectionStatus(Math.random() > 0.3 ? 'success' : 'error');
      setIsTestingConnection(false);
    }, 2000);
  };

  const renderApiSettings = () => (
  <div className="space-y-6 text-gray-200">
      {/* Telegram Bot Settings */}
  <div className="rounded-lg p-6 bg-gradient-to-br from-blue-600/15 via-blue-500/10 to-cyan-500/10 border border-blue-400/20 shadow-elevated-sm">
        <div className="flex items-center space-x-2 mb-4">
          <Bot className="w-5 h-5 text-blue-300" />
          <h3 className="text-sm font-semibold text-gray-100 tracking-wide">Telegram Bot</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-[11px] font-medium text-gray-300 mb-2 uppercase tracking-wide">
              Bot Token
            </label>
            <div className="relative">
              <input
                type={showKeys.telegram_bot_token ? 'text' : 'password'}
                value={formData.telegram_bot_token}
                onChange={(e) => handleInputChange('telegram_bot_token', e.target.value)}
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
                name="telegram_bot_token"
                className="w-full p-3 pr-12 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 transition-colors text-sm placeholder:text-gray-500"
                placeholder="Введите Bot Token"
              />
              <button
                type="button"
                onClick={() => toggleShowKey('telegram_bot_token')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-200"
              >
                {showKeys.telegram_bot_token ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-surface-100/50 border border-white/5">
            <p className="text-[11px] text-gray-400 leading-relaxed">
              <strong>Как создать Telegram бота:</strong><br />
              1. Найдите @BotFather в Telegram<br />
              2. Отправьте команду /newbot<br />
              3. Следуйте инструкциям для создания бота<br />
              4. Скопируйте полученный Bot Token и вставьте его сюда
            </p>
          </div>
        </div>
      </div>

      {/* OpenRouter API Settings */}
  <div className="rounded-lg p-6 bg-gradient-to-br from-purple-600/15 via-indigo-600/10 to-blue-600/10 border border-purple-400/20 shadow-elevated-sm">
        <div className="flex items-center space-x-2 mb-4">
          <Database className="w-5 h-5 text-purple-300" />
          <h3 className="text-sm font-semibold text-gray-100 tracking-wide">OpenRouter API</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-[11px] font-medium text-gray-300 mb-2 uppercase tracking-wide">
              API Key
            </label>
            <div className="relative">
              <input
                type={showKeys.openrouter_api_key ? 'text' : 'password'}
                value={formData.openrouter_api_key}
                onChange={(e) => handleInputChange('openrouter_api_key', e.target.value)}
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
                name="openrouter_api_key"
                className="w-full p-3 pr-12 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-purple-500/60 focus:border-purple-500/60 transition-colors text-sm placeholder:text-gray-500"
                placeholder="Введите OpenRouter API Key"
              />
              <button
                type="button"
                onClick={() => toggleShowKey('openrouter_api_key')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-200"
              >
                {showKeys.openrouter_api_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-surface-100/50 border border-white/5">
            <p className="text-[11px] text-gray-400 leading-relaxed">
              <strong>OpenRouter</strong> предоставляет доступ к различным AI-моделям для анализа чатов и генерации ответов.<br />
              Получите API ключ на <a href="https://openrouter.ai" className="underline" target="_blank" rel="noopener noreferrer">openrouter.ai</a>
            </p>
          </div>
        </div>
      </div>

      {/* Save and Test Buttons */}
  <div className="flex items-center space-x-4">
  <button onClick={handleSaveApiConfig} className="px-6 py-2 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white text-sm shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 transition-all flex items-center space-x-2">
          <Save className="w-4 h-4" />
          <span>Сохранить настройки</span>
        </button>

  <button onClick={testConnection} disabled={isTestingConnection} className="px-6 py-2 rounded-lg bg-surface-100/60 border border-white/5 text-gray-300 text-sm hover:bg-surface-100/80 transition-colors flex items-center space-x-2 disabled:opacity-40">
          <Database className={`w-4 h-4 ${isTestingConnection ? 'animate-spin' : ''}`} />
          <span>{isTestingConnection ? 'Тестирование...' : 'Тест подключения'}</span>
        </button>

        {connectionStatus && (
          <div className={`flex items-center space-x-2 ${connectionStatus === 'success' ? 'text-emerald-400' : 'text-red-400'}`}>
            {connectionStatus === 'success' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <span className="text-xs font-medium">
              {connectionStatus === 'success' 
                ? 'Подключение успешно!' 
                : 'Ошибка подключения'
              }
            </span>
          </div>
        )}
      </div>
    </div>
  );

  const renderPromptsSettings = () => (
  <div className="space-y-6 text-gray-200">
  <div className="rounded-lg p-6 bg-surface-100/60 border border-white/5 shadow-elevated-sm">
        <div className="flex items-center space-x-2 mb-4">
          <Bot className="w-5 h-5 text-purple-300" />
          <h3 className="text-sm font-semibold text-gray-100 tracking-wide">Настройка промптов для AI</h3>
          {isLoadingPrompts && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-300"></div>
          )}
        </div>
        
        <div className="space-y-6">
          <div>
            <label className="block text-[11px] font-medium text-gray-400 mb-2 uppercase tracking-wide">
              Промпт для резюмирования диалогов
            </label>
            <textarea
              value={prompts.summary}
              onChange={(e) => setPrompts({ ...prompts, summary: e.target.value })}
              className="w-full p-3 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-purple-500/60 focus:border-purple-500/60 transition-colors text-sm placeholder:text-gray-500"
              rows={3}
              placeholder="Введите промпт для создания резюме диалогов..."
            />
            <p className="text-[10px] text-gray-500 mt-1">
              Этот промпт используется для создания краткого резюме переписки
            </p>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-gray-400 mb-2 uppercase tracking-wide">
              Промпт для предложения ответов
            </label>
            <textarea
              value={prompts.suggestions}
              onChange={(e) => setPrompts({ ...prompts, suggestions: e.target.value })}
              className="w-full p-3 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-purple-500/60 focus:border-purple-500/60 transition-colors text-sm placeholder:text-gray-500"
              rows={3}
              placeholder="Введите промпт для генерации предложенных ответов..."
            />
            <p className="text-[10px] text-gray-500 mt-1">
              Этот промпт используется для создания вариантов ответов
            </p>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-gray-400 mb-2 uppercase tracking-wide">
              Промпт для анализа диалога
            </label>
            <textarea
              value={prompts.analysis}
              onChange={(e) => setPrompts({ ...prompts, analysis: e.target.value })}
              className="w-full p-3 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-purple-500/60 focus:border-purple-500/60 transition-colors text-sm placeholder:text-gray-500"
              rows={3}
              placeholder="Введите промпт для анализа диалога..."
            />
            <p className="text-[10px] text-gray-500 mt-1">
              Этот промпт используется для анализа настроения и рекомендаций
            </p>
          </div>

          <div className="p-4 rounded-lg bg-surface-200/40 border border-white/5">
            <h4 className="text-xs font-medium text-gray-300 mb-2">Доступные переменные:</h4>
            <div className="text-[10px] text-gray-500 space-y-1">
              <p><code className="bg-purple-100 px-1 rounded">{'{{messages}}'}</code> - История сообщений</p>
              <p><code className="bg-purple-100 px-1 rounded">{'{{contact_name}}'}</code> - Имя собеседника</p>
              <p><code className="bg-purple-100 px-1 rounded">{'{{contact_info}}'}</code> - Информация о контакте</p>
              <p><code className="bg-purple-100 px-1 rounded">{'{{chat_type}}'}</code> - Тип чата (личный/группа)</p>
            </div>
          </div>

          <div className="flex space-x-4">
            <button 
              onClick={savePrompts} 
              disabled={isSavingPrompts}
              className="px-6 py-2 rounded-lg bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 text-white text-sm shadow-glow-blue hover:from-purple-500 hover:via-indigo-500 hover:to-blue-500 transition-all flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className={`w-4 h-4 ${isSavingPrompts ? 'animate-spin' : ''}`} />
              <span>{isSavingPrompts ? 'Сохранение...' : 'Сохранить промпты'}</span>
            </button>

            <button onClick={() => { setPrompts({ summary: 'Создай краткое резюме этого диалога, выделив ключевые моменты и общий тон беседы.', suggestions: 'Предложи 3-4 варианта ответов на основе контекста диалога.', analysis: 'Проанализируй настроение собеседника и дай рекомендации по дальнейшему общению.' }); }} className="px-6 py-2 rounded-lg bg-surface-100/60 border border-white/5 text-gray-300 text-sm hover:bg-surface-100/80 transition-colors">
              Сбросить к умолчанию
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderKeywordsSettings = () => (
    <div className="space-y-6 text-gray-200">
      <div className="rounded-lg p-6 bg-surface-100/60 border border-white/5 shadow-elevated-sm">
        <div className="flex items-center space-x-2 mb-5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-inner-glow">
            <ListPlus className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-100 tracking-wide">Ключевые слова для мониторинга</h3>
            <p className="text-[11px] text-gray-400 mt-1">Будут выделяться и подсчитываться в групповых сообщениях. Наблюдайте активность прямо в карточках чатов и списке участников.</p>
          </div>
        </div>
        <div className="flex gap-2 mb-5">
          <input
            value={newKeyword}
            onChange={e => setNewKeyword(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addKeyword(); } }}
            placeholder="Новое слово..."
            className="flex-1 p-3 rounded-lg bg-surface-200/50 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-sm placeholder:text-gray-500"
          />
          <button
            onClick={addKeyword}
            className="px-5 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 text-white text-sm font-medium shadow-glow-blue"
          >Добавить</button>
        </div>
        {keywords.length === 0 && <div className="text-[11px] text-gray-500">Список пуст. Добавьте первое ключевое слово.</div>}
        {keywords.length > 0 && (
          <ul className="flex flex-wrap gap-2">
            {keywords.map(k => (
              <li key={k} className="group flex items-center gap-1 pl-2 pr-1 py-1 rounded-md bg-white/5 border border-white/10 text-[11px] text-gray-300 shadow-sm">
                <span className="tracking-wide">{k}</span>
                <button
                  onClick={() => removeKeyword(k)}
                  className="opacity-60 group-hover:opacity-100 hover:text-red-300 p-0.5 rounded"
                  aria-label="Удалить ключевое слово"
                >
                  <X className="w-3 h-3" />
                </button>
              </li>
            ))}
          </ul>
        )}

  {/* Bulk Import */}
  <BulkKeywordImport keywords={keywords} setKeywords={setKeywords} />
      </div>
    </div>
  );

  const renderModelsSettings = () => (
    <div className="space-y-6 text-gray-100">
      <div className="rounded-xl p-6 bg-gradient-to-br from-purple-500/15 via-indigo-500/10 to-blue-500/15 border border-white/10 shadow-glow-blue">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500/60 to-indigo-500/60 flex items-center justify-center shadow-inner-glow">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold tracking-wide text-white/95">Выбор AI моделей OpenRouter</h3>
              <p className="text-[11px] text-white/70">Подберите оптимальные модели для текста, изображений и аудио</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadAvailableModels}
              disabled={isLoadingModels}
              className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-white/90 flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${isLoadingModels ? 'animate-spin' : ''}`} />
              {isLoadingModels ? 'Загрузка...' : 'Обновить'}
            </button>
            <button
              onClick={loadBalance}
              disabled={isLoadingBalance}
              className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-white/90 flex items-center gap-2 disabled:opacity-50"
            >
              <Database className={`w-3 h-3 ${isLoadingBalance ? 'animate-spin' : ''}`} />
              {isLoadingBalance ? 'Загрузка...' : 'Баланс'}
            </button>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2.5 mb-4">
          <span className="text-[11px] text-white/60 mr-1">Категории:</span>
          <span className="text-[10px] px-2 py-1 rounded-md border border-blue-400/30 bg-blue-500/15 text-blue-100">Text · {(availableModels.text||[]).length}</span>
          <span className="text-[10px] px-2 py-1 rounded-md border border-violet-400/30 bg-violet-500/15 text-violet-100">Vision · {(availableModels.image_vision||[]).length}</span>
          <span className="text-[10px] px-2 py-1 rounded-md border border-pink-400/30 bg-pink-500/15 text-pink-100">Generation · {(availableModels.image_generation||[]).length}</span>
          <span className="text-[10px] px-2 py-1 rounded-md border border-amber-400/30 bg-amber-500/15 text-amber-100">Audio · {(availableModels.audio||[]).length}</span>
        </div>

        {/* Balance Info */}
        {balance && (
          <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-emerald-500/15 via-teal-500/15 to-green-500/15 border border-emerald-400/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] text-white/70">Баланс аккаунта</p>
                <p className="text-lg font-semibold text-emerald-200">{balance.formatted_balance}</p>
                {balance.balance === 0 && balance.usage === 0 && (
                  <p className="text-[10px] text-amber-200 mt-1">
                    Баланс недоступен. Возможно, требуется платный план OpenRouter.
                  </p>
                )}
              </div>
              <div>
                <p className="text-[11px] text-white/70">Использовано</p>
                <p className="text-sm text-white/80">{balance.formatted_usage}</p>
                <p className="text-[10px] text-white/60 mt-1">
                  Проверьте баланс на <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-200">openrouter.ai</a>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Model Selection - Organized by Categories */}
        <div className="space-y-6">
          {/* Reusable searchable select */}
          {(() => {
            type Model = { id: string; name: string; provider?: string; pricing?: any; description?: string; capabilities?: string[]; context_length?: number };

            const ModelSelect: React.FC<{
              label: string;
              placeholder: string;
              models: Model[];
              value: string;
              onChange: (id: string) => void;
              colorScheme?: 'blue' | 'violet' | 'pink' | 'amber';
            }> = ({ label, placeholder, models, value, onChange, colorScheme = 'blue' }) => {
              const [open, setOpen] = useState(false);
              const [query, setQuery] = useState('');
              const containerRef = useRef<HTMLDivElement | null>(null);

              const colorClasses = {
                blue: 'focus-within:ring-blue-500/60 focus-within:border-blue-500/60',
                violet: 'focus-within:ring-violet-500/60 focus-within:border-violet-500/60',
                pink: 'focus-within:ring-pink-500/60 focus-within:border-pink-500/60',
                amber: 'focus-within:ring-amber-500/60 focus-within:border-amber-500/60'
              };

              const filtered = useMemo(() => {
                if (!query.trim()) return models;
                const q = query.toLowerCase();
                return models.filter(m =>
                  (m.name || '').toLowerCase().includes(q) ||
                  (m.id || '').toLowerCase().includes(q) ||
                  (m.provider || '').toLowerCase().includes(q) ||
                  (m.capabilities || []).some(c => c.toLowerCase().includes(q))
                );
              }, [models, query]);

              useEffect(() => {
                const handler = (e: MouseEvent) => {
                  if (!containerRef.current) return;
                  if (!containerRef.current.contains(e.target as Node)) setOpen(false);
                };
                document.addEventListener('mousedown', handler);
                return () => document.removeEventListener('mousedown', handler);
              }, []);

              const selected = value ? models.find(m => m.id === value) : undefined;

              return (
                <div className="w-full" ref={containerRef}>
                  <label className="block text-[11px] font-medium text-gray-400 mb-2 uppercase tracking-wide">{label}</label>
                  <div className="relative">
                    <div
                      className={`flex items-center gap-2 p-2.5 rounded-lg bg-surface-100/60 border border-white/5 focus-within:ring-2 ${colorClasses[colorScheme]} transition-colors text-sm cursor-text ${open ? `ring-2 ${colorClasses[colorScheme].replace('focus-within:', '').replace('/60', '/40')}` : ''}`}
                      onClick={() => setOpen(true)}
                    >
                      <Search className="w-4 h-4 text-gray-400" />
                      <input
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        placeholder={selected ? `${selected.name} — ${selected.provider} (in: ${selected.pricing?.prompt_cost || 'N/A'} / out: ${selected.pricing?.completion_cost || 'N/A'})` : placeholder}
                        className="flex-1 bg-transparent outline-none placeholder:text-gray-500"
                      />
                      {selected && (
                        <span className="hidden sm:inline text-[10px] px-2 py-0.5 rounded border border-white/10 text-gray-400">
                          {selected.id}
                        </span>
                      )}
                    </div>

                    {open && (
                      <div className="absolute z-[9999] mt-1 w-full rounded-lg bg-surface-0/95 backdrop-blur-md border border-white/10 shadow-elevated-sm max-h-72 overflow-auto">
                        {filtered.length === 0 && (
                          <div className="p-3 text-[12px] text-gray-500">Ничего не найдено</div>
                        )}
                        {filtered.map(m => (
                          <button
                            key={m.id}
                            type="button"
                            onClick={() => { onChange(m.id); setOpen(false); setQuery(''); }}
                            className={`w-full text-left px-3 py-2.5 hover:bg-white/5 transition-colors ${m.id === value ? 'bg-white/5' : ''}`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="min-w-0">
                                <div className="text-[13px] text-gray-200 truncate font-medium">{m.name}</div>
                                <div className="text-[11px] text-gray-500 truncate">{m.provider} · {m.id}</div>
                                <div className="mt-1 flex flex-wrap items-center gap-1.5">
                                  {(() => {
                                    const { inputs, outputs } = getCapabilityTags(m.capabilities);
                                    return (
                                      <>
                                        <div className="flex items-center gap-1.5">
                                          {inputs.map((inp, idx) => (
                                            <span key={`in-${inp.label}-${idx}`} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-400/30">
                                              <inp.icon className="w-3 h-3" />
                                              {inp.label}
                                            </span>
                                          ))}
                                        </div>
                                        {(inputs.length > 0 || outputs.length > 0) && (
                                          <ArrowRight className="w-3 h-3 text-gray-400" />
                                        )}
                                        <div className="flex items-center gap-1.5">
                                          {outputs.map((outp, idx) => (
                                            <span key={`out-${outp.label}-${idx}`} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-200 border border-blue-400/30">
                                              <outp.icon className="w-3 h-3" />
                                              {outp.label}
                                            </span>
                                          ))}
                                        </div>
                                      </>
                                    );
                                  })()}
                                </div>
                              </div>
                              <div className="text-right shrink-0">
                                <div className="text-[11px] text-gray-300">
                                  <div>In: {m.pricing?.prompt_cost || 'N/A'}</div>
                                  <div>Out: {m.pricing?.completion_cost || 'N/A'}</div>
                                </div>
                                {typeof m.context_length === 'number' && m.context_length > 0 && (
                                  <div className="text-[10px] text-gray-500">Context: {m.context_length}</div>
                                )}
                              </div>
                            </div>
                            {m.description && (
                              <div className="mt-1 text-[11px] text-gray-500 line-clamp-2">{m.description}</div>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
          </div>

                  {/* Selected model compact info */}
                  {selected && (
                    <div className="mt-2 p-3 rounded-lg bg-surface-200/40 border border-white/5">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="text-[12px] text-gray-200 font-medium truncate">{selected.name}</div>
                          <div className="text-[11px] text-gray-500 truncate">{selected.provider} · {selected.id}</div>
                          <div className="mt-1 flex flex-wrap items-center gap-1.5">
                            {(() => {
                              const { inputs, outputs } = getCapabilityTags(selected.capabilities);
                              return (
                                <>
                                  <div className="flex items-center gap-1.5">
                                    {inputs.map((inp, idx) => (
                                      <span key={`sin-${inp.label}-${idx}`} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-400/30">
                                        <inp.icon className="w-3 h-3" />
                                        {inp.label}
                                      </span>
                                    ))}
                                  </div>
                                  {(inputs.length > 0 || outputs.length > 0) && (
                                    <ArrowRight className="w-3 h-3 text-gray-400" />
                                  )}
                                  <div className="flex items-center gap-1.5">
                                    {outputs.map((outp, idx) => (
                                      <span key={`sout-${outp.label}-${idx}`} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-200 border border-blue-400/30">
                                        <outp.icon className="w-3 h-3" />
                                        {outp.label}
                                      </span>
                                    ))}
                                  </div>
                                  {typeof selected.context_length === 'number' && selected.context_length > 0 && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded border border-white/10 text-gray-400">ctx {selected.context_length}</span>
                                  )}
                                </>
                              );
                            })()}
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="text-[11px] text-gray-300">
                            <div>In: {selected.pricing?.prompt_cost || 'N/A'}</div>
                            <div>Out: {selected.pricing?.completion_cost || 'N/A'}</div>
                          </div>
                        </div>
                      </div>
                      {selected.description && (
                        <div className="mt-2 text-[11px] text-gray-500 line-clamp-2">{selected.description}</div>
                      )}
                    </div>
                  )}
                </div>
              );
            };

            // helper findSelected больше не используется

            return (
              <>
                {/* Text Models Section */}
                <div className="rounded-lg p-5 bg-gradient-to-br from-blue-600/10 via-blue-500/5 to-cyan-500/5 border border-blue-400/20">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/40 to-cyan-500/40 flex items-center justify-center">
                      <Search className="w-4 h-4 text-blue-300" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-100 tracking-wide">Модели для работы с текстом</h4>
                      <p className="text-[11px] text-gray-400">Анализ сообщений, генерация ответов и обработка текста</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <ModelSelect
                      label="Основная текстовая модель"
                      placeholder="Поиск модели по названию, провайдеру или возможности..."
                      models={availableModels.text as any}
                      value={selectedModels.text}
                      onChange={(newValue) => {
                        setSelectedModels(prev => ({ ...prev, text: newValue }));
                        if (newValue) saveSelectedModel('text', newValue);
                      }}
                      colorScheme="blue"
                    />
                    <p className="text-[10px] text-blue-300/80">Модель для анализа текстовых сообщений и генерации ответов</p>
                  </div>
                </div>

                {/* Image Models Section */}
                <div className="rounded-lg p-5 bg-gradient-to-br from-violet-600/10 via-pink-500/5 to-purple-500/5 border border-violet-400/20">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500/40 to-pink-500/40 flex items-center justify-center">
                      <Eye className="w-4 h-4 text-violet-300" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-100 tracking-wide">Модели для работы с изображениями</h4>
                      <p className="text-[11px] text-gray-400">Анализ изображений и генерация новых изображений</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <ModelSelect
                      label="Модель для анализа изображений (Vision)"
                      placeholder="Поиск vision-модели..."
                      models={availableModels.image_vision as any}
                      value={selectedModels.image_vision}
                      onChange={(newValue) => {
                        setSelectedModels(prev => ({ ...prev, image_vision: newValue }));
                        if (newValue) saveSelectedModel('image_vision', newValue);
                      }}
                      colorScheme="violet"
                    />
                    <p className="text-[10px] text-violet-300/80">Модель для анализа и описания изображений</p>

                    <ModelSelect
                      label="Модель для генерации изображений"
                      placeholder="Поиск модели генерации изображений..."
                      models={availableModels.image_generation as any}
                      value={selectedModels.image_generation}
                      onChange={(newValue) => {
                        setSelectedModels(prev => ({ ...prev, image_generation: newValue }));
                        if (newValue) saveSelectedModel('image_generation', newValue);
                      }}
                      colorScheme="pink"
                    />
                    <p className="text-[10px] text-pink-300/80">Модель для создания изображений по тексту</p>
                  </div>
                </div>

                {/* Audio Models Section */}
                <div className="rounded-lg p-5 bg-gradient-to-br from-amber-600/10 via-orange-500/5 to-yellow-500/5 border border-amber-400/20">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500/40 to-orange-500/40 flex items-center justify-center">
                      <Volume2 className="w-4 h-4 text-amber-300" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-100 tracking-wide">Модели для работы с аудио</h4>
                      <p className="text-[11px] text-gray-400">Транскрипция и анализ голосовых сообщений</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <ModelSelect
                      label="Аудио модель"
                      placeholder="Поиск аудио-модели..."
                      models={availableModels.audio as any}
                      value={selectedModels.audio}
                      onChange={(newValue) => {
                        setSelectedModels(prev => ({ ...prev, audio: newValue }));
                        if (newValue) saveSelectedModel('audio', newValue);
                      }}
                      colorScheme="amber"
                    />
                    <p className="text-[10px] text-amber-300/80">Модель для транскрипции и анализа голосовых сообщений</p>
                  </div>
                </div>
              </>
            );
          })()}
        </div>

        {/* Info Block */}
        <div className="mt-6 p-4 rounded-lg bg-white/5 border border-white/10">
          <h4 className="text-xs font-semibold text-white/80 mb-2">Информация о моделях</h4>
          <div className="text-[11px] text-white/65 space-y-1.5">
            <p>• Модели автоматически сохраняются при выборе</p>
            <p>• <span className="text-violet-300 font-medium">Vision</span> анализирует изображения (вход: изображение → выход: текст)</p>
            <p>• <span className="text-pink-300 font-medium">Generation</span> создаёт изображения (вход: текст → выход: изображение)</p>
            <p>• Цены указаны за 1M токенов (In: входящие, Out: исходящие)</p>
            <p>• Требуется действующий API ключ OpenRouter</p>
            <p>• Возможны ограничения по регионам у некоторых провайдеров</p>
          </div>
        </div>

        {isLoadingModels && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-purple-300" />
            <span className="ml-2 text-sm text-white/70">Загрузка доступных моделей...</span>
          </div>
        )}
      </div>
    </div>
  );

  // Удалены вкладки "Уведомления", "Внешний вид", "Безопасность"

  const renderTabContent = () => {
    switch (activeTab) {
      case 'api':
        return renderApiSettings();
      case 'models':
        return renderModelsSettings();
      case 'prompts':
        return renderPromptsSettings();
      case 'keywords':
        return renderKeywordsSettings();
      default:
        return renderApiSettings();
    }
  };

  return (
    <div className="flex-1 bg-surface-0 text-gray-200 overflow-hidden">
      <div className="flex h-full">
        {/* Settings Navigation */}
        <div className="w-64 bg-surface-50/70 border-r border-white/5 p-4 hidden lg:block shadow-elevated-sm">
          <h1 className="text-lg font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-cyan-200 to-purple-300 mb-6">Настройки</h1>
          <nav className="space-y-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors text-sm ${activeTab === tab.id ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-glow-blue' : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'}`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Mobile Navigation */}
        <div className="lg:hidden w-full bg-surface-50/70 border-b border-white/5 p-4 shadow-elevated-sm">
          <h1 className="text-lg font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-cyan-200 to-purple-300 mb-4">Настройки</h1>
          <select
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value as typeof activeTab)}
            className="w-full p-3 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-sm"
          >
            {tabs.map(tab => (
              <option key={tab.id} value={tab.id}>
                {tab.label}
              </option>
            ))}
          </select>
        </div>

        {/* Settings Content */}
  <div className="flex-1 overflow-y-auto p-4 lg:p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default Settings;