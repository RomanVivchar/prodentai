import React, { useState, useEffect } from 'react';
import { Clock, Plus, Trash2, Bell, BellOff, X, MessageCircle, CheckCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface Reminder {
  id: number;
  type?: string;  // For backward compatibility
  reminder_type?: string;  // From API
  time: string;
  date?: string;
  message: string;
  is_active: boolean;
  created_at?: string;
}

const Reminders: React.FC = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [showTelegramOverlay, setShowTelegramOverlay] = useState(false);
  const [telegramId, setTelegramId] = useState('');
  const [checkingTelegram, setCheckingTelegram] = useState(false);
  const [isTelegramLinked, setIsTelegramLinked] = useState(false);
  const [newReminder, setNewReminder] = useState({
    type: 'morning_hygiene',
    time: '08:00',
    date: '',
    message: ''
  });
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<number | null>(null);

  const reminderTypes = [
    {
      id: 'morning_hygiene',
      name: 'Утренняя гигиена',
      description: 'Напоминание о чистке зубов утром',
      icon: '🌅'
    },
    {
      id: 'evening_hygiene',
      name: 'Вечерняя гигиена',
      description: 'Напоминание о чистке зубов вечером',
      icon: '🌙'
    },
    {
      id: 'dental_visit',
      name: 'Визит к стоматологу',
      description: 'Напоминание о запланированном визите',
      icon: '🦷'
    },
    {
      id: 'floss',
      name: 'Использование зубной нити',
      description: 'Напоминание о чистке межзубных промежутков',
      icon: '🧵'
    }
  ];

  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      const id = parseInt(storedUserId);
      setUserId(id);
      checkTelegramRegistration(id);
      fetchReminders(id);
    } else {
      setLoading(false);
      toast.error('Пожалуйста, войдите в систему');
    }
  }, []);

  const checkTelegramRegistration = async (user_id: number) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/users/check-telegram/${user_id}`
      );
      if (response.ok) {
        const data = await response.json();
        setIsTelegramLinked(data.registered);
        if (!data.registered) {
          setShowTelegramOverlay(true);
        }
      }
    } catch (error) {
      console.error('Error checking Telegram registration:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReminders = async (user_id: number) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/reminders/user/${user_id}`
      );
      if (response.ok) {
        const data = await response.json();
        // Map reminder_type to type for compatibility
        const mappedData = data.map((reminder: any) => ({
          ...reminder,
          type: reminder.reminder_type || reminder.type
        }));
        setReminders(mappedData);
      }
    } catch (error) {
      console.error('Error fetching reminders:', error);
    }
  };

  const handleLinkTelegram = async () => {
    if (!telegramId || !userId) {
      toast.error('Введите Telegram ID');
      return;
    }

    const telegramIdNum = parseInt(telegramId);
    if (isNaN(telegramIdNum)) {
      toast.error('Telegram ID должен быть числом');
      return;
    }

    setCheckingTelegram(true);
    try {
      // Сначала привязываем telegram_id
      const linkResponse = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/users/link-telegram/${userId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ telegram_id: telegramIdNum }),
        }
      );

      if (linkResponse.ok) {
        // Проверяем, что пользователь зарегистрирован в боте
        const checkResponse = await fetch(
          `${process.env.REACT_APP_API_URL || '/api'}/users/check-telegram/${userId}`
        );
        
        if (checkResponse.ok) {
          const checkData = await checkResponse.json();
          if (checkData.registered) {
            setIsTelegramLinked(true);
            setShowTelegramOverlay(false);
            toast.success('Telegram успешно подключен!');
            fetchReminders(userId);
          } else {
            toast.error('Пожалуйста, сначала нажмите /start в Telegram-боте');
          }
        }
      } else {
        const errorData = await linkResponse.json();
        toast.error(errorData.detail || 'Ошибка привязки Telegram');
      }
    } catch (error) {
      console.error('Error linking Telegram:', error);
      toast.error('Ошибка привязки Telegram');
    } finally {
      setCheckingTelegram(false);
    }
  };

  const handleAddReminder = async () => {
    if (!userId) {
      toast.error('Пожалуйста, войдите в систему');
      return;
    }

    const reminderType = reminderTypes.find(t => t.id === newReminder.type);
    const defaultMessage = reminderType?.description || '';
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/reminders/create`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            reminder_type: newReminder.type,
            time: newReminder.time,
            date: newReminder.type === 'dental_visit' ? newReminder.date : undefined,
            message: newReminder.message || defaultMessage,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Map reminder_type to type for compatibility
        const mappedData = {
          ...data,
          type: data.reminder_type || data.type
        };
        setReminders(prev => [...prev, mappedData]);
        setShowAddForm(false);
        setNewReminder({ type: 'morning_hygiene', time: '08:00', date: '', message: '' });
        toast.success('Напоминание добавлено');
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Ошибка создания напоминания');
      }
    } catch (error) {
      console.error('Error creating reminder:', error);
      toast.error('Ошибка создания напоминания');
    }
  };

  const toggleReminder = async (id: number) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/reminders/toggle/${id}`,
        {
          method: 'PUT',
        }
      );

      if (response.ok) {
        const data = await response.json();
        setReminders(prev =>
          prev.map(reminder =>
            reminder.id === id
              ? { ...reminder, is_active: data.is_active }
              : reminder
          )
        );
        toast.success(data.is_active ? 'Напоминание включено' : 'Напоминание отключено');
      } else {
        toast.error('Ошибка обновления напоминания');
      }
    } catch (error) {
      console.error('Error toggling reminder:', error);
      toast.error('Ошибка обновления напоминания');
    }
  };

  const deleteReminder = async (id: number) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || '/api'}/reminders/${id}`,
        {
          method: 'DELETE',
        }
      );

      if (response.ok) {
        setReminders(prev => prev.filter(reminder => reminder.id !== id));
        toast.success('Напоминание удалено');
      } else {
        toast.error('Ошибка удаления напоминания');
      }
    } catch (error) {
      console.error('Error deleting reminder:', error);
      toast.error('Ошибка удаления напоминания');
    }
  };

  const getReminderTypeInfo = (type: string) => {
    return reminderTypes.find(t => t.id === type) || reminderTypes[0];
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-dental-600" />
          <p>Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Telegram Overlay */}
      {showTelegramOverlay && !isTelegramLinked && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setShowTelegramOverlay(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
            
            <div className="text-center mb-6">
              <MessageCircle className="h-16 w-16 text-dental-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Подключите Telegram-бота
              </h2>
              <p className="text-gray-600">
                Для использования напоминаний необходимо подключить Telegram-бота
              </p>
            </div>

            <div className="space-y-4 mb-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">Инструкция:</h3>
                <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
                  <li>Откройте Telegram и найдите бота</li>
                  <li>Нажмите кнопку "Открыть бота" ниже</li>
                  <li>Нажмите /start в боте</li>
                  <li>Введите ваш Telegram ID в поле ниже</li>
                  <li>Нажмите "Подключить"</li>
                </ol>
              </div>

              <div>
                <label className="form-label">Ваш Telegram ID</label>
                <input
                  type="text"
                  value={telegramId}
                  onChange={(e) => setTelegramId(e.target.value)}
                  placeholder="Например: 123456789"
                  className="form-input"
                />
                <a
                  href="https://t.me/userinfobot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-dental-600 hover:text-dental-700 mt-1 inline-flex items-center"
                >
                  Как узнать Telegram ID? Откройте бота @userinfobot →
                </a>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <a
                href="https://t.me/ProDentAIbot"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary w-full text-center inline-flex items-center justify-center"
              >
                <MessageCircle className="h-5 w-5 mr-2" />
                Открыть бота
              </a>
              
              <button
                onClick={handleLinkTelegram}
                disabled={checkingTelegram || !telegramId}
                className="btn-secondary w-full inline-flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {checkingTelegram ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Проверка...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Подключить
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Напоминания о гигиене</h1>
        <p className="text-lg text-gray-600">Формирование здоровых привычек с помощью уведомлений</p>
      </div>

      {/* Add Reminder Button */}
      {isTelegramLinked && (
        <div className="mb-6">
          <button
            onClick={() => setShowAddForm(true)}
            className="btn-primary inline-flex items-center"
          >
            <Plus className="h-5 w-5 mr-2" />
            Добавить напоминание
          </button>
        </div>
      )}

      {/* Add Reminder Form */}
      {showAddForm && isTelegramLinked && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Новое напоминание</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="form-label">Тип напоминания</label>
              <select
                value={newReminder.type}
                onChange={(e) => setNewReminder(prev => ({ ...prev, type: e.target.value, date: '' }))}
                className="form-input"
              >
                {reminderTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="form-label">Время</label>
              <input
                type="time"
                value={newReminder.time}
                onChange={(e) => setNewReminder(prev => ({ ...prev, time: e.target.value }))}
                className="form-input"
              />
            </div>
          </div>

          {newReminder.type === 'dental_visit' && (
            <div className="mb-4">
              <label className="form-label">Дата визита</label>
              <input
                type="date"
                value={newReminder.date}
                onChange={(e) => setNewReminder(prev => ({ ...prev, date: e.target.value }))}
                min={new Date().toISOString().split('T')[0]}
                className="form-input"
              />
            </div>
          )}
          
          <div className="mb-4">
            <label className="form-label">Сообщение (необязательно)</label>
            <textarea
              value={newReminder.message}
              onChange={(e) => setNewReminder(prev => ({ ...prev, message: e.target.value }))}
              placeholder="Например: Доброе утро! Пора освежить улыбку 😊"
              className="form-input h-20"
            />
          </div>
          
          <div className="flex gap-4">
            <button onClick={handleAddReminder} className="btn-primary">
              Добавить
            </button>
            <button 
              onClick={() => setShowAddForm(false)} 
              className="btn-secondary"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {/* Reminders List */}
      <div className="space-y-4">
        {reminders.length === 0 ? (
          <div className="card text-center py-12">
            <Clock className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Нет напоминаний</h3>
            <p className="text-gray-600 mb-4">
              {isTelegramLinked 
                ? 'Добавьте напоминания для формирования здоровых привычек'
                : 'Подключите Telegram-бота для использования напоминаний'}
            </p>
            {isTelegramLinked && (
              <button
                onClick={() => setShowAddForm(true)}
                className="btn-primary"
              >
                Добавить первое напоминание
              </button>
            )}
          </div>
        ) : (
          reminders.map(reminder => {
            const reminderType = reminder.type || reminder.reminder_type || 'morning_hygiene';
            const typeInfo = getReminderTypeInfo(reminderType);
            return (
              <div key={reminder.id} className="card">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="text-2xl mr-4">{typeInfo.icon}</div>
                    <div>
                      <h3 className="text-lg font-semibold">{typeInfo.name}</h3>
                      <p className="text-gray-600">{reminder.message}</p>
                      <div className="flex items-center gap-4 mt-1">
                        <p className="text-sm text-gray-500">
                          🕐 Время: {reminder.time}
                        </p>
                        {reminder.date && (
                          <p className="text-sm text-gray-500">
                            📅 Дата: {new Date(reminder.date).toLocaleDateString('ru-RU')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleReminder(reminder.id)}
                      className={`p-2 rounded-lg transition-colors ${
                        reminder.is_active
                          ? 'bg-green-100 text-green-600 hover:bg-green-200'
                          : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                      }`}
                    >
                      {reminder.is_active ? (
                        <Bell className="h-5 w-5" />
                      ) : (
                        <BellOff className="h-5 w-5" />
                      )}
                    </button>
                    
                    <button
                      onClick={() => deleteReminder(reminder.id)}
                      className="p-2 text-red-500 hover:bg-red-100 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                
                <div className="mt-4 flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-2 ${
                    reminder.is_active ? 'bg-green-500' : 'bg-gray-300'
                  }`}></div>
                  <span className="text-sm text-gray-600">
                    {reminder.is_active ? 'Активно' : 'Отключено'}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Statistics */}
      {isTelegramLinked && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card text-center">
            <h3 className="text-2xl font-bold text-dental-600 mb-2">
              {reminders.length}
            </h3>
            <p className="text-gray-600">Всего напоминаний</p>
          </div>
          
          <div className="card text-center">
            <h3 className="text-2xl font-bold text-green-600 mb-2">
              {reminders.filter(r => r.is_active).length}
            </h3>
            <p className="text-gray-600">Активных</p>
          </div>
          
          <div className="card text-center">
            <h3 className="text-2xl font-bold text-blue-600 mb-2">
              {reminderTypes.length}
            </h3>
            <p className="text-gray-600">Типов напоминаний</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reminders;
