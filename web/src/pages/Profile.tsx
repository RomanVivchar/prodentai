import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const Profile: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          navigate('/login');
          return;
        }

        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const userId = localStorage.getItem('user_id');
        
        if (!userId) {
          // Попробуем получить через /me
          const meResponse = await fetch(`${apiUrl}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (meResponse.ok) {
            const meData = await meResponse.json();
            localStorage.setItem('user_id', meData.id.toString());
            const profileResponse = await fetch(`${apiUrl}/api/users/profile/${meData.id}`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });
            if (profileResponse.ok) {
              setUser(await profileResponse.json());
            }
          } else {
            navigate('/login');
          }
        } else {
          const response = await fetch(`${apiUrl}/api/users/profile/${userId}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            setUser(await response.json());
          } else if (response.status === 401) {
            navigate('/login');
          }
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
        toast.error('Ошибка загрузки профиля');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    toast.success('Выход выполнен');
    navigate('/');
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center">
          <p>Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center">
          <p>Профиль не найден</p>
          <button onClick={() => navigate('/login')} className="btn-primary mt-4">
            Войти
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold mb-6">Профиль</h1>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <p className="text-gray-900">{user.email || 'Не указан'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Имя</label>
            <p className="text-gray-900">{user.first_name || 'Не указано'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Фамилия</label>
            <p className="text-gray-900">{user.last_name || 'Не указано'}</p>
          </div>
          {user.telegram_id && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Telegram ID</label>
              <p className="text-gray-900">{user.telegram_id}</p>
            </div>
          )}
          <div className="pt-4">
            <button onClick={handleLogout} className="btn-secondary">
              Выйти
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;

