import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Stethoscope, Home, Shield, Apple, Heart, Clock, Lightbulb, Braces, X, Menu } from 'lucide-react';

const Navbar: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Главная', icon: Home },
    { path: '/risks', label: 'Риски', icon: Shield },
    { path: '/nutrition', label: 'Питание', icon: Apple },
    { path: '/psychology', label: 'Психология', icon: Heart },
    { path: '/reminders', label: 'Напоминания', icon: Clock },
    { path: '/facts', label: 'Факты', icon: Lightbulb },
    { path: '/braces', label: 'Брекеты', icon: Braces },
  ];

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <Stethoscope className="h-8 w-8 text-dental-600" />
            <span className="text-xl font-bold text-gray-800">ProDentAI</span>
          </Link>

          {/* Navigation Items */}
          <div className="hidden md:flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-dental-100 text-dental-700'
                      : 'text-gray-600 hover:text-dental-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Auth buttons */}
          <div className="flex items-center space-x-4">
            {localStorage.getItem('user_id') ? (
              <Link
                to="/profile"
                className="btn-secondary text-sm"
              >
                Профиль
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-dental-600 text-sm font-medium"
                >
                  Войти
                </Link>
                <Link
                  to="/register"
                  className="btn-primary text-sm"
                >
                  Регистрация
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button 
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-gray-600 hover:text-dental-600 focus:outline-none focus:ring-2 focus:ring-dental-500 rounded-md p-2"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        <div 
          className={`md:hidden border-t border-gray-200 overflow-hidden transition-all duration-300 ease-in-out ${
            isMobileMenuOpen 
              ? 'max-h-screen opacity-100 py-4' 
              : 'max-h-0 opacity-0 py-0'
          }`}
        >
          <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center space-x-2 px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-dental-100 text-dental-700'
                        : 'text-gray-600 hover:text-dental-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              
              {/* Mobile auth buttons */}
              <div className="pt-4 border-t border-gray-200 mt-2">
                {localStorage.getItem('user_id') ? (
                  <Link
                    to="/profile"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
                  >
                    Профиль
                  </Link>
                ) : (
                  <div className="flex flex-col space-y-2">
                    <Link
                      to="/login"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="flex items-center justify-center px-4 py-2 text-gray-600 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
                    >
                      Войти
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="flex items-center justify-center px-4 py-2 bg-dental-600 text-white rounded-md text-sm font-medium hover:bg-dental-700 transition-colors"
                    >
                      Регистрация
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
      </div>
    </nav>
  );
};

export default Navbar;
