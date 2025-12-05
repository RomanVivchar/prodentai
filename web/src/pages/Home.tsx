import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Apple, Heart, Clock, Lightbulb, Braces, ArrowRight } from 'lucide-react';

const Home: React.FC = () => {
  const features = [
    {
      title: 'Оценка рисков',
      description: 'Персональная карта стоматологических рисков на основе ваших данных',
      icon: Shield,
      path: '/risks',
      color: 'bg-red-500'
    },
    {
      title: 'Анализ питания',
      description: 'Контроль пищевых привычек, влияющих на здоровье зубов',
      icon: Apple,
      path: '/nutrition',
      color: 'bg-green-500'
    },
    {
      title: 'Психологическая поддержка',
      description: 'Помощь в снижении тревоги перед визитом к стоматологу',
      icon: Heart,
      path: '/psychology',
      color: 'bg-pink-500'
    },
    {
      title: 'Напоминания',
      description: 'Формирование здоровых привычек с помощью уведомлений',
      icon: Clock,
      path: '/reminders',
      color: 'bg-blue-500'
    },
    {
      title: 'Факты о гигиене',
      description: 'Ежедневное просвещение о стоматологическом здоровье',
      icon: Lightbulb,
      path: '/facts',
      color: 'bg-yellow-500'
    },
    {
      title: 'Помощь с брекетами',
      description: 'Ситуационная помощь пользователям с брекет-системами',
      icon: Braces,
      path: '/braces',
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          ProDentAI
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Персональный ИИ-компаньон для проактивного поддержания стоматологического здоровья
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/risks"
            className="btn-primary inline-flex items-center px-6 py-3 text-lg"
          >
            Начать оценку рисков
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <Link
            to="/facts"
            className="btn-secondary inline-flex items-center px-6 py-3 text-lg"
          >
            Узнать интересные факты
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Link
              key={index}
              to={feature.path}
              className="card hover:shadow-lg transition-shadow duration-300 group"
            >
              <div className="flex items-center mb-4">
                <div className={`${feature.color} p-3 rounded-lg mr-4`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 group-hover:text-dental-600 transition-colors">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600 mb-4">{feature.description}</p>
              <div className="flex items-center text-dental-600 font-medium group-hover:text-dental-700">
                Подробнее
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          );
        })}
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="stat-card">
          <h3 className="text-2xl font-bold mb-2">6</h3>
          <p className="text-blue-100">Функциональных модулей</p>
        </div>
        <div className="stat-card">
          <h3 className="text-2xl font-bold mb-2">24/7</h3>
          <p className="text-blue-100">Доступность помощи</p>
        </div>
        <div className="stat-card">
          <h3 className="text-2xl font-bold mb-2">AI</h3>
          <p className="text-blue-100">Искусственный интеллект</p>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-dental-50 rounded-lg p-8 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Готовы начать заботу о зубах?
        </h2>
        <p className="text-lg text-gray-600 mb-6">
          Присоединяйтесь к тысячам пользователей, которые уже используют ProDentAI
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/risks"
            className="btn-primary inline-flex items-center px-8 py-3 text-lg"
          >
            Начать прямо сейчас
          </Link>
          <a
            href="https://t.me/ProDentAIbot"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary inline-flex items-center px-8 py-3 text-lg"
          >
            Telegram-бот
          </a>
        </div>
      </div>
    </div>
  );
};

export default Home;
