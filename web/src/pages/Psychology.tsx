import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Lightbulb, History } from 'lucide-react';
import toast from 'react-hot-toast';

const Psychology: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'tips' | 'history'>('chat');
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{type: 'user' | 'ai', message: string}>>([]);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

  const tips = [
    {
      title: 'Дыхательные упражнения',
      content: 'Попробуйте технику 4-7-8: вдох на 4 счета, задержка на 7, выдох на 8. Это поможет снизить тревогу.',
      icon: '🫁'
    },
    {
      title: 'Музыка и отвлечение',
      content: 'Возьмите наушники и слушайте любимую музыку во время процедуры. Это поможет отвлечься.',
      icon: '🎵'
    },
    {
      title: 'Общение с врачом',
      content: 'Не стесняйтесь говорить о своих страхах. Хороший стоматолог всегда готов объяснить и поддержать.',
      icon: '👨‍⚕️'
    },
    {
      title: 'Постепенное знакомство',
      content: 'Если очень боитесь, начните с простого осмотра. Это поможет привыкнуть к атмосфере клиники.',
      icon: '🦷'
    }
  ];

  useEffect(() => {
    // Получаем user_id из localStorage или регистрируем пользователя
    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(parseInt(storedUserId));
    } else {
      // Если нет user_id, создаем временного пользователя для демо
      // В реальном приложении нужно перенаправить на регистрацию
      toast.error('Пожалуйста, зарегистрируйтесь для использования психолога');
    }
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    if (!userId) {
      toast.error('Пожалуйста, зарегистрируйтесь для использования психолога');
      return;
    }

    const userMessageText = message.trim();
    
    // Add user message to chat
    const userMessage = { type: 'user' as const, message: userMessageText };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      // Вызываем реальный API (используем относительный путь)
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/psychology/chat`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            message: userMessageText,
            session_type: 'general',
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        const aiMessage = { type: 'ai' as const, message: data.ai_response };
        setChatHistory(prev => [...prev, aiMessage]);
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Ошибка при отправке сообщения');
        // Показываем сообщение об ошибке в чате
        const errorMessage = { type: 'ai' as const, message: 'Извините, произошла ошибка. Попробуйте еще раз.' };
        setChatHistory(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Ошибка подключения к серверу');
      const errorMessage = { type: 'ai' as const, message: 'Ошибка подключения. Проверьте, что сервер запущен.' };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Психологическая поддержка</h1>
        <p className="text-lg text-gray-600">Помощь в снижении тревоги перед визитом к стоматологу</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('chat')}
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'chat'
              ? 'border-dental-600 text-dental-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <MessageCircle className="h-4 w-4 inline mr-2" />
          Диалог
        </button>
        <button
          onClick={() => setActiveTab('tips')}
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'tips'
              ? 'border-dental-600 text-dental-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Lightbulb className="h-4 w-4 inline mr-2" />
          Советы
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'history'
              ? 'border-dental-600 text-dental-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <History className="h-4 w-4 inline mr-2" />
          История
        </button>
      </div>

      {/* Chat Tab */}
      {activeTab === 'chat' && (
        <div className="card">
          <div className="flex items-center mb-6">
            <Heart className="h-8 w-8 text-pink-500 mr-3" />
            <div>
              <h2 className="text-xl font-semibold">Чат с психологом</h2>
              <p className="text-gray-600">Расскажите о своих переживаниях, я помогу вам справиться с тревогой</p>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 mb-4 bg-gray-50">
            {chatHistory.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Начните диалог, написав о своих переживаниях</p>
                {!userId && (
                  <p className="text-sm text-red-500 mt-2">
                    Для использования психолога необходимо зарегистрироваться
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {chatHistory.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.type === 'user'
                          ? 'bg-dental-600 text-white'
                          : 'bg-white text-gray-800 border border-gray-200'
                      }`}
                    >
                      <p className="text-sm">{msg.message}</p>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-600">Печатает</span>
                        <div className="flex space-x-1">
                          <span className="animate-bounce text-gray-600" style={{ animationDelay: '0ms' }}>.</span>
                          <span className="animate-bounce text-gray-600" style={{ animationDelay: '150ms' }}>.</span>
                          <span className="animate-bounce text-gray-600" style={{ animationDelay: '300ms' }}>.</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Message Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Напишите о своих переживаниях..."
              className="form-input flex-1"
            />
            <button
              onClick={handleSendMessage}
              disabled={!message.trim() || loading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Отправка...' : 'Отправить'}
            </button>
          </div>
        </div>
      )}

      {/* Tips Tab */}
      {activeTab === 'tips' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {tips.map((tip, index) => (
            <div key={index} className="card">
              <div className="flex items-start">
                <div className="text-3xl mr-4">{tip.icon}</div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">{tip.title}</h3>
                  <p className="text-gray-600">{tip.content}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">История сессий</h2>
          {chatHistory.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <History className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>У вас пока нет истории сессий</p>
            </div>
          ) : (
            <div className="space-y-4">
              {chatHistory.map((msg, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-sm font-medium ${
                      msg.type === 'user' ? 'text-dental-600' : 'text-gray-600'
                    }`}>
                      {msg.type === 'user' ? 'Вы' : 'Психолог'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date().toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-700">{msg.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Psychology;
