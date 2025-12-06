import React, { useState, useEffect } from 'react';
import { Apple, Camera, Upload, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const Nutrition: React.FC = () => {
  const [analysisType, setAnalysisType] = useState<'text' | 'photo' | null>(null);
  const [foodDescription, setFoodDescription] = useState('');
  const [weightGrams, setWeightGrams] = useState<string>('');
  const [volumeMl, setVolumeMl] = useState<string>('');
  // Новые поля
  const [accompanyingFoods, setAccompanyingFoods] = useState<string>('');
  const [consumptionDuration, setConsumptionDuration] = useState<string>('');
  const [waterAfter, setWaterAfter] = useState<boolean | null>(null);
  const [sugarAdded, setSugarAdded] = useState<string>('');
  const [temperature, setTemperature] = useState<string>('');
  const [acidityCategory, setAcidityCategory] = useState<string>('');
  const [sensitivityAfter, setSensitivityAfter] = useState<boolean | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    // Получаем user_id из localStorage
    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(parseInt(storedUserId));
    } else {
      toast.error('Пожалуйста, зарегистрируйтесь для использования анализа питания');
    }
  }, []);

  const handleTextAnalysis = async () => {
    if (!foodDescription.trim()) return;
    if (!userId) {
      toast.error('Пожалуйста, зарегистрируйтесь для использования анализа питания');
      return;
    }

    setLoading(true);
    try {
      // Используем относительный путь для избежания проблем с CORS и протоколами
      const apiUrl = process.env.REACT_APP_API_URL || '/api';
      
      // Формируем полное описание с учетом сопутствующих продуктов
      const fullDescription = accompanyingFoods 
        ? `${foodDescription}. Сопутствующие продукты: ${accompanyingFoods}`
        : foodDescription;
      
      const response = await fetch(`${apiUrl}/nutrition/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          food_description: fullDescription,
          weight_grams: weightGrams ? parseFloat(weightGrams) : null,
          volume_ml: volumeMl ? parseFloat(volumeMl) : null,
          accompanying_foods: accompanyingFoods || null,
          consumption_duration: consumptionDuration || null,
          water_after: waterAfter,
          sugar_added: sugarAdded || null,
          temperature: temperature || null,
          acidity_category: acidityCategory || null,
          sensitivity_after: sensitivityAfter,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка при анализе');
      }

      const data = await response.json();
      
      // Фильтруем предлоги и неправильные формы из food_items
      const prepositions = ['с', 'в', 'на', 'для', 'и', 'или', 'из', 'от', 'к', 'по', 'под', 'над', 'при', 'про', 'без', 'через'];
      const categoryWords = ['сопутствующие', 'продукты', 'основные', 'блюдо', 'блюда'];
      const rawFoodItems = data.analysis_result?.food_items || [];
      const filteredFoodItems = rawFoodItems
        .map((item: string) => item.trim().replace(/[.,;:!?]+$/, '')) // Убираем знаки препинания в конце
        .filter((item: string) => {
          const itemLower = item.toLowerCase().trim();
          // Исключаем предлоги, категории, пустые строки и строки, заканчивающиеся на ":"
          return itemLower.length > 1 && 
                 !prepositions.includes(itemLower) && 
                 !categoryWords.includes(itemLower) &&
                 !itemLower.endsWith(':') &&
                 !itemLower.includes('сопутствующие');
        });
      
      // Преобразуем ответ API в формат для отображения
      const summaryValue = data.summary || data.analysis_result?.summary;
      console.log('Summary from API:', summaryValue);
      console.log('Full data:', data);
      
      setAnalysisResult({
        food_items: filteredFoodItems,
        sugar_content: data.sugar_content || 0,
        acidity_level: data.acidity_level || 7.0,
        health_score: data.analysis_result?.health_score || 5.0,
        weight_grams: data.weight_grams,
        volume_ml: data.volume_ml,
        analysis_result: data.analysis_result || {}, // Сохраняем весь analysis_result, включая summary
        summary: summaryValue, // Сохраняем summary на верхнем уровне
        recommendations: data.recommendations 
          ? data.recommendations.split('; ').filter((r: string) => r.trim())
          : data.analysis_result?.recommendations || [],
      });
      
      toast.success('Анализ завершен!');
    } catch (error: any) {
      console.error('Error analyzing nutrition:', error);
      toast.error(error.message || 'Ошибка при анализе питания');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!userId) {
      toast.error('Пожалуйста, зарегистрируйтесь для использования анализа питания');
      return;
    }

    // Проверка размера файла (макс 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Размер файла не должен превышать 10MB');
      return;
    }

    // Проверка типа файла
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Поддерживаются только изображения: JPG, PNG, WEBP');
      return;
    }

    setLoading(true);
    try {
      // Используем относительный путь для избежания проблем с CORS и протоколами
      const apiUrl = process.env.REACT_APP_API_URL || '/api';
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${apiUrl}/nutrition/analyze-image?user_id=${userId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка при анализе изображения');
      }

      const data = await response.json();
      
      // Фильтруем предлоги и неправильные формы из food_items
      const prepositions = ['с', 'в', 'на', 'для', 'и', 'или', 'из', 'от', 'к', 'по', 'под', 'над', 'при', 'про', 'без', 'через'];
      const categoryWords = ['сопутствующие', 'продукты', 'основные', 'блюдо', 'блюда'];
      const rawFoodItems = (data.analysis_result?.food_items || data.analysis_result?.detected_foods || []);
      const filteredFoodItems = rawFoodItems
        .map((item: string) => item.trim().replace(/[.,;:!?]+$/, '')) // Убираем знаки препинания в конце
        .filter((item: string) => {
          const itemLower = item.toLowerCase().trim();
          // Исключаем предлоги, категории, пустые строки и строки, заканчивающиеся на ":"
          return itemLower.length > 1 && 
                 !prepositions.includes(itemLower) && 
                 !categoryWords.includes(itemLower) &&
                 !itemLower.endsWith(':') &&
                 !itemLower.includes('сопутствующие');
        });
      
      // Преобразуем ответ API в формат для отображения
      const analysis = data.analysis_result || {};
      setAnalysisResult({
        food_items: filteredFoodItems,
        sugar_content: analysis.sugar_content || 0,
        acidity_level: analysis.acidity_level || 7.0,
        health_score: analysis.health_score || 5.0,
        weight_grams: data.weight_grams,
        volume_ml: data.volume_ml,
        analysis_result: analysis, // Сохраняем весь analysis_result, включая summary
        summary: data.summary || analysis.summary, // Сохраняем summary на верхнем уровне
        recommendations: analysis.recommendations || [],
      });
      
      toast.success('Анализ изображения завершен!');
    } catch (error: any) {
      console.error('Error analyzing image:', error);
      toast.error(error.message || 'Ошибка при анализе изображения');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Анализ питания</h1>
        <p className="text-lg text-gray-600">Контроль пищевых привычек, влияющих на здоровье зубов</p>
      </div>

      {!analysisType && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div
            onClick={() => setAnalysisType('text')}
            className="card hover:shadow-lg transition-shadow cursor-pointer group"
          >
            <div className="flex items-center mb-4">
              <div className="bg-green-500 p-3 rounded-lg mr-4">
                <Apple className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 group-hover:text-dental-600 transition-colors">
                Описать еду
              </h3>
            </div>
            <p className="text-gray-600 mb-4">
              Опишите что вы ели или планируете съесть для анализа влияния на зубы
            </p>
            <div className="text-dental-600 font-medium group-hover:text-dental-700">
              Начать анализ →
            </div>
          </div>

          <div
            onClick={() => setAnalysisType('photo')}
            className="card hover:shadow-lg transition-shadow cursor-pointer group"
          >
            <div className="flex items-center mb-4">
              <div className="bg-blue-500 p-3 rounded-lg mr-4">
                <Camera className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 group-hover:text-dental-600 transition-colors">
                Анализ фото
              </h3>
            </div>
            <p className="text-gray-600 mb-4">
              Загрузите фото еды для автоматического анализа с помощью ИИ
            </p>
            <div className="text-dental-600 font-medium group-hover:text-dental-700">
              Загрузить фото →
            </div>
          </div>
        </div>
      )}

      {analysisType === 'text' && !analysisResult && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Опишите что вы ели</h2>
          <textarea
            value={foodDescription}
            onChange={(e) => setFoodDescription(e.target.value)}
            placeholder="Например: яблоко, печенье, кофе с сахаром..."
            className="form-input h-32 mb-4"
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Вес (граммы) - опционально
              </label>
              <input
                type="number"
                value={weightGrams}
                onChange={(e) => setWeightGrams(e.target.value)}
                placeholder="Например: 200"
                min="0"
                step="0.1"
                className="form-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Объем (мл) - опционально
              </label>
              <input
                type="number"
                value={volumeMl}
                onChange={(e) => setVolumeMl(e.target.value)}
                placeholder="Например: 250"
                min="0"
                step="0.1"
                className="form-input"
              />
            </div>
          </div>

          {/* Новые поля */}
          <div className="space-y-6 mb-4">
            {/* 1. Сопутствующие продукты */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-3">
                Есть ли сопутствующие продукты?
              </label>
              <input
                type="text"
                value={accompanyingFoods}
                onChange={(e) => setAccompanyingFoods(e.target.value)}
                placeholder="Например: печенье + чай"
                className="form-input border-2 border-gray-300 rounded-lg px-4 py-2.5 focus:border-dental-500 focus:ring-2 focus:ring-dental-200 transition-all w-full"
              />
              <p className="text-xs text-gray-500 mt-1">Сахар + кислота = взрыв для эмали</p>
            </div>

            {/* 2. Длительность употребления */}
            <div>
              <label className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                <span className="text-2xl mr-2">⏳</span>
                Вы употребили это быстро или растянуто?
              </label>
              <div className="grid grid-cols-3 gap-3">
                {['быстро', '5-10 мин', 'долго, больше 15 мин'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setConsumptionDuration(option)}
                    className={`px-4 py-3 rounded-lg border-2 transition-all font-medium ${
                      consumptionDuration === option
                        ? 'border-dental-500 bg-dental-50 text-dental-700 shadow-md'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-dental-300 hover:bg-dental-50'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">Критично для леденцов, сладких напитков, энергетиков</p>
            </div>

            {/* 3. Вода после */}
            <div>
              <label className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                <span className="text-2xl mr-2">💧</span>
                Пили ли воду после этого?
              </label>
              <div className="flex gap-3">
                {[
                  { value: true, label: 'Да', icon: '✅' },
                  { value: false, label: 'Нет', icon: '❌' }
                ].map((option) => (
                  <button
                    key={String(option.value)}
                    type="button"
                    onClick={() => setWaterAfter(option.value)}
                    className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all font-medium ${
                      waterAfter === option.value
                        ? 'border-green-500 bg-green-50 text-green-700 shadow-md'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-green-300 hover:bg-green-50'
                    }`}
                  >
                    <span className="text-lg mr-2">{option.icon}</span>
                    {option.label}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">Это в разы уменьшает риски</p>
            </div>

            {/* 4. Сахар */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-3">
                Сахар добавляли?
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['нет', '1 ложка', '2 ложки', 'больше'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setSugarAdded(option)}
                    className={`px-4 py-3 rounded-lg border-2 transition-all font-medium ${
                      sugarAdded === option
                        ? 'border-yellow-500 bg-yellow-50 text-yellow-700 shadow-md'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-yellow-300 hover:bg-yellow-50'
                    }`}
                  >
                    {option === 'нет' ? '🚫' : option === '1 ложка' ? '1️⃣' : option === '2 ложки' ? '2️⃣' : '⚠️'} {option}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">Важно для чая, кофе, напитков</p>
            </div>

            {/* 5. Температура */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-3">
                Температура:
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'холодная', icon: '❄️', color: 'blue' },
                  { value: 'комнатная', icon: '🌡️', color: 'gray' },
                  { value: 'горячая', icon: '🔥', color: 'red' }
                ].map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setTemperature(option.value)}
                    className={`px-4 py-3 rounded-lg border-2 transition-all font-medium ${
                      temperature === option.value
                        ? `border-${option.color}-500 bg-${option.color}-50 text-${option.color}-700 shadow-md`
                        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                  >
                            <span className="text-2xl mb-1">{option.icon}</span>
                    <span className="text-sm">{option.value}</span>
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">Влияет на чувствительность и микротрещины</p>
            </div>

            {/* 6. Кислотность */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-3">
                Это:
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'кислое', icon: '🍋', color: 'orange' },
                  { value: 'сладкое', icon: '🍬', color: 'pink' },
                  { value: 'нейтральное', icon: '🥛', color: 'gray' }
                ].map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setAcidityCategory(acidityCategory === option.value ? '' : option.value)}
                    className={`px-4 py-3 rounded-lg border-2 transition-all font-medium ${
                      acidityCategory === option.value
                        ? `border-${option.color}-500 bg-${option.color}-50 text-${option.color}-700 shadow-md`
                        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                  >
                            <span className="text-2xl mb-1">{option.icon}</span>
                    <span className="text-sm">{option.value}</span>
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">Не просим pH — просто категория</p>
            </div>

            {/* 7. Чувствительность */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-3">
                Испытываете ли вы чувствительность после употребления?
              </label>
              <div className="flex gap-3">
                {[
                  { value: true, label: 'Да', icon: '⚠️', color: 'red' },
                  { value: false, label: 'Нет', icon: '✅', color: 'green' }
                ].map((option) => (
                  <button
                    key={String(option.value)}
                    type="button"
                    onClick={() => setSensitivityAfter(option.value)}
                    className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all font-medium ${
                      sensitivityAfter === option.value
                        ? `border-${option.color}-500 bg-${option.color}-50 text-${option.color}-700 shadow-md`
                        : `border-gray-300 bg-white text-gray-700 hover:border-${option.color}-300 hover:bg-${option.color}-50`
                    }`}
                  >
                    <span className="text-lg mr-2">{option.icon}</span>
                    {option.label}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">Если человек после энергетика ощутил чувствительность — сильный маркер</p>
            </div>
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={handleTextAnalysis}
              disabled={!foodDescription.trim() || loading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Анализ...' : 'Анализировать'}
            </button>
            <button
              onClick={() => {
                setAnalysisType(null);
                setFoodDescription('');
                setWeightGrams('');
                setVolumeMl('');
                setAccompanyingFoods('');
                setConsumptionDuration('');
                setWaterAfter(null);
                setSugarAdded('');
                setTemperature('');
                setAcidityCategory('');
                setSensitivityAfter(null);
              }}
              className="btn-secondary"
            >
              Назад
            </button>
          </div>
        </div>
      )}

      {analysisType === 'photo' && !analysisResult && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Загрузите фото еды</h2>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">Перетащите фото сюда или нажмите для выбора</p>
            <input
              type="file"
              accept="image/*"
              onChange={handlePhotoUpload}
              className="hidden"
              id="photo-upload"
              disabled={loading}
            />
            <label
              htmlFor="photo-upload"
              className={`btn-primary cursor-pointer inline-block ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {loading ? 'Анализ...' : 'Выбрать файл'}
            </label>
          </div>
          <div className="flex gap-4 mt-4">
            <button
              onClick={() => setAnalysisType(null)}
              className="btn-secondary"
            >
              Назад
            </button>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all animate-fade-in">
            <div className="flex flex-col items-center justify-center">
              {/* Animated Spinner */}
              <div className="relative mb-6">
                <Loader2 className="h-16 w-16 text-dental-600 animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-12 w-12 bg-dental-100 rounded-full animate-pulse"></div>
                </div>
              </div>
              
              {/* Loading Text */}
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Анализируем еду...
              </h3>
              <p className="text-gray-600 text-center mb-4">
                Искусственный интеллект обрабатывает информацию о вашем блюде
              </p>
              
              {/* Progress Dots */}
              <div className="flex space-x-2">
                <div className="h-2 w-2 bg-dental-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="h-2 w-2 bg-dental-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="h-2 w-2 bg-dental-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {analysisResult && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Результаты анализа</h2>
            
            {/* Краткое описание блюда */}
            {(analysisResult.summary || analysisResult.analysis_result?.summary) && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-dental-500 p-4 rounded-lg mb-6">
                <h3 className="font-semibold text-gray-800 mb-2 flex items-center">
                  <span className="text-lg mr-2">📝</span>
                  Описание блюда
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {analysisResult.summary || analysisResult.analysis_result?.summary}
                </p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="font-semibold text-yellow-800 mb-2 text-sm">Сахар (г)</h3>
                <p className="text-2xl font-bold text-yellow-600">{analysisResult.sugar_content || 0}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2 text-sm">Здоровье</h3>
                <p className="text-2xl font-bold text-green-600">{analysisResult.health_score || 0}/10</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2 text-sm">Кислотность (pH)</h3>
                <p className="text-2xl font-bold text-purple-600">{analysisResult.acidity_level?.toFixed(1) || '7.0'}</p>
              </div>
            </div>

            {/* Пользовательские параметры */}
            {(analysisResult.weight_grams || analysisResult.volume_ml) && (
              <div className="grid grid-cols-2 gap-4 mb-6">
                {analysisResult.weight_grams && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800 mb-2 text-sm">Вес</h3>
                    <p className="text-2xl font-bold text-gray-700">{analysisResult.weight_grams} г</p>
                  </div>
                )}
                {analysisResult.volume_ml && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800 mb-2 text-sm">Объем</h3>
                    <p className="text-2xl font-bold text-gray-700">{analysisResult.volume_ml} мл</p>
                  </div>
                )}
              </div>
            )}

            <div className="mb-6">
              <h3 className="font-semibold mb-3">Обнаруженные продукты:</h3>
              <div className="flex flex-wrap gap-2">
                {analysisResult.food_items?.map((item: string, index: number) => (
                  <span key={index} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                    {item}
                  </span>
                ))}
                {analysisResult.detected_foods?.map((item: string, index: number) => (
                  <span key={index} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <h3 className="font-semibold mb-3">Рекомендации:</h3>
              <div className="space-y-2">
                {analysisResult.recommendations.map((rec: string, index: number) => (
                  <div key={index} className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5" />
                    <span className="text-gray-700">{rec}</span>
                  </div>
                ))}
              </div>
            </div>

            {analysisResult.sugar_content > 20 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertTriangle className="h-5 w-5 text-red-500 mr-3" />
                  <div>
                    <h4 className="font-semibold text-red-800">Высокое содержание сахара!</h4>
                    <p className="text-red-700">Рекомендуем прополоскать рот после еды</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="text-center">
            <button
              onClick={() => {
                setAnalysisResult(null);
                setAnalysisType(null);
                setFoodDescription('');
                setWeightGrams('');
                setVolumeMl('');
                setAccompanyingFoods('');
                setConsumptionDuration('');
                setWaterAfter(null);
                setSugarAdded('');
                setTemperature('');
                setAcidityCategory('');
                setSensitivityAfter(null);
              }}
              className="btn-primary"
            >
              Новый анализ
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Nutrition;
