import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const RiskAssessment: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    // Получаем user_id из localStorage
    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(parseInt(storedUserId));
    }
  }, []);

  const questionCategories = [
    {
      category: '🧬 Наследственность',
      questions: [
        {
          id: 'family_gum_problems',
          question: 'Были ли у ваших родителей/родственников проблемы с деснами или ранняя потеря зубов?',
          type: 'radio',
          options: ['Да', 'Нет', 'Не знаю']
        },
        {
          id: 'family_weak_enamel',
          question: 'Есть ли у кого-то в семье слабая эмаль или частый кариес?',
          type: 'radio',
          options: ['Да', 'Нет', 'Не знаю']
        },
        {
          id: 'family_bruxism',
          question: 'Замечали ли вы или родственники скрежет зубами (бруксизм)?',
          type: 'radio',
          options: ['Да', 'Нет', 'Не знаю']
        }
      ]
    },
    {
      category: '🍏 Питание и привычки',
      questions: [
        {
          id: 'sweet_drinks',
          question: 'Как часто вы пьёте сладкие напитки (чай/кофе с сахаром, газировка, сок)?',
          type: 'radio',
          options: ['Ежедневно', 'Несколько раз в неделю', 'Редко', 'Никогда']
        },
        {
          id: 'acidic_foods',
          question: 'Как часто вы употребляете кислые продукты/напитки (цитрусовые, энергетики, газировка)?',
          type: 'radio',
          options: ['Ежедневно', 'Несколько раз в неделю', 'Редко', 'Никогда']
        },
        {
          id: 'snacking_frequency',
          question: 'Сколько раз в день перекусываете?',
          type: 'radio',
          options: ['Постоянно', '3-4 раза', '1-2 раза', 'Не перекусываю']
        },
        {
          id: 'eating_before_sleep',
          question: 'Едите ли вы перед сном (за 2 часа до него)?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Никогда']
        },
        {
          id: 'water_after_meals',
          question: 'Пьёте ли воду после еды?',
          type: 'radio',
          options: ['Всегда', 'Часто', 'Иногда', 'Редко']
        }
      ]
    },
    {
      category: '🪥 Гигиена',
      questions: [
        {
          id: 'brushing_frequency',
          question: 'Как часто вы чистите зубы?',
          type: 'radio',
          options: ['2 раза в день', '1 раз в день', 'Через день', 'Реже']
        },
        {
          id: 'floss_usage',
          question: 'Используете ли зубную нить или ирригатор?',
          type: 'radio',
          options: ['Ежедневно', 'Несколько раз в неделю', 'Редко', 'Никогда']
        },
        {
          id: 'brushing_duration',
          question: 'Как долго длится ваша чистка?',
          type: 'radio',
          options: ['Меньше 1 мин', '1–2 мин', 'Более 2 мин']
        },
        {
          id: 'electric_brush',
          question: 'Используете ли электрическую щетку?',
          type: 'radio',
          options: ['Да', 'Нет']
        }
      ]
    },
    {
      category: '😬 Зубные привычки и нагрузки',
      questions: [
        {
          id: 'teeth_clenching',
          question: 'Сжимаете ли вы зубы или скрипите ими (днём или ночью)?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Никогда']
        },
        {
          id: 'mouth_breathing',
          question: 'Дышите ли вы ртом или храпите?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Никогда']
        },
        {
          id: 'hard_objects',
          question: 'Жуёте ли вы твёрдые предметы (семечки, орехи, ногти)?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Никогда']
        },
        {
          id: 'jaw_discomfort',
          question: 'Есть ли у вас щёлканье или дискомфорт в челюстном суставе?',
          type: 'radio',
          options: ['Да', 'Иногда', 'Нет']
        }
      ]
    },
    {
      category: '💧 Слюноотделение и здоровье',
      questions: [
        {
          id: 'dry_mouth',
          question: 'Бывает ли сухость во рту утром или днём?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Никогда']
        },
        {
          id: 'medications_dry_mouth',
          question: 'Принимаете ли вы лекарства, вызывающие сухость во рту (антидепрессанты, антигистамины и т.п.)?',
          type: 'radio',
          options: ['Да', 'Нет', 'Не знаю']
        },
        {
          id: 'reflux',
          question: 'Есть ли у вас рефлюкс/изжога?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Нет']
        }
      ]
    },
    {
      category: '🦷 Состояние десен и зубов',
      questions: [
        {
          id: 'bleeding_gums',
          question: 'Кровоточат ли ваши десны при чистке?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Никогда']
        },
        {
          id: 'sensitivity',
          question: 'Есть ли чувствительность на холодное/горячее?',
          type: 'radio',
          options: ['Да, сильная', 'Умеренная', 'Слабая', 'Нет']
        },
        {
          id: 'bad_breath',
          question: 'Есть ли неприятный запах или ощущение воспаления десен?',
          type: 'radio',
          options: ['Да, часто', 'Иногда', 'Редко', 'Нет']
        }
      ]
    }
  ];

  // Flatten questions for navigation
  const questions = questionCategories.flatMap(cat => cat.questions);

  const getRiskLevel = (score: number) => {
    if (score < 0.3) return { level: 'green', label: 'Низкий риск' };
    if (score < 0.6) return { level: 'yellow', label: 'Средний риск' };
    return { level: 'red', label: 'Высокий риск' };
  };

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const nextStep = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!userId) {
      toast.error('Пожалуйста, зарегистрируйтесь для прохождения оценки рисков');
      return;
    }

    setLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/risks/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          questionnaire_data: answers,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка при оценке рисков');
      }

      const data = await response.json();
      setResults(data);
      setShowResults(true);
      toast.success('Оценка рисков завершена!');
    } catch (error: any) {
      console.error('Error assessing risks:', error);
      toast.error(error.message || 'Ошибка при оценке рисков');
    } finally {
      setLoading(false);
    }
  };

  const resetAssessment = () => {
    setCurrentStep(0);
    setAnswers({});
    setShowResults(false);
    setResults(null);
  };

  // Loading overlay
  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all animate-fade-in">
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="h-16 w-16 text-dental-600 animate-spin mb-6" />
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Анализируем ваши ответы...
            </h3>
            <p className="text-gray-600 text-center">
              Искусственный интеллект создает персональную карту рисков
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (showResults && results) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Результаты оценки рисков</h1>
          <p className="text-lg text-gray-600">Ваша персональная карта стоматологических рисков</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {Object.entries(results.risk_scores || {}).map(([risk, score]: [string, any]) => {
            const riskInfo = getRiskLevel(score);
            const riskLabels: Record<string, string> = {
              cavity_risk: 'Риск кариеса',
              gum_disease_risk: 'Риск заболеваний десен',
              sensitivity_risk: 'Риск чувствительности',
              enamel_erosion_risk: 'Риск эрозии эмали'
            };

            return (
              <div key={risk} className={`risk-card ${riskInfo.level}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">{riskLabels[risk] || risk}</h3>
                  <div className="flex items-center">
                    {riskInfo.level === 'green' && <CheckCircle className="h-5 w-5 text-green-500" />}
                    {riskInfo.level === 'yellow' && <AlertTriangle className="h-5 w-5 text-yellow-500" />}
                    {riskInfo.level === 'red' && <XCircle className="h-5 w-5 text-red-500" />}
                  </div>
                </div>
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Риск</span>
                    <span>{Math.round(score * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        riskInfo.level === 'green' ? 'bg-green-500' :
                        riskInfo.level === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${score * 100}%` }}
                    ></div>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{riskInfo.label}</p>
              </div>
            );
          })}
        </div>

        <div className="card mb-8">
          <h3 className="text-xl font-semibold mb-4">Персонализированные рекомендации</h3>
          <ul className="space-y-3">
            {results.recommendations && results.recommendations.length > 0 ? (
              results.recommendations.map((rec: string, index: number) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{rec}</span>
                </li>
              ))
            ) : (
              <li className="text-gray-600">Рекомендации будут добавлены в ближайшее время</li>
            )}
          </ul>
        </div>

        <div className="text-center">
          <button
            onClick={resetAssessment}
            className="btn-primary"
          >
            Пройти оценку заново
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentStep];
  const currentCategory = questionCategories.find(cat => 
    cat.questions.some(q => q.id === currentQuestion.id)
  );

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Оценка стоматологических рисков</h1>
        <p className="text-lg text-gray-600 mb-6">
          Ответьте на несколько вопросов для получения персональной оценки
        </p>
        {currentCategory && (
          <div className="mb-4">
            <span className="text-sm font-semibold text-dental-600 bg-dental-50 px-3 py-1 rounded-full">
              {currentCategory.category}
            </span>
          </div>
        )}
        <div className="flex justify-center mb-6">
          <div className="flex space-x-2">
            {questions.map((_, index) => (
              <div
                key={index}
                className={`h-2 w-8 rounded-full ${
                  index <= currentStep ? 'bg-dental-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
        <p className="text-sm text-gray-500">
          Вопрос {currentStep + 1} из {questions.length}
        </p>
      </div>

      <div className="card">
        <div className="flex items-center mb-6">
          <Shield className="h-8 w-8 text-dental-600 mr-3" />
          <h2 className="text-xl font-semibold">{currentQuestion.question}</h2>
        </div>

        <div className="space-y-3">
          {currentQuestion.options.map((option, index) => (
            <label
              key={index}
              className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <input
                type="radio"
                name={currentQuestion.id}
                value={option}
                checked={answers[currentQuestion.id] === option}
                onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
                className="mr-3"
              />
              <span className="text-gray-700">{option}</span>
            </label>
          ))}
        </div>

        <div className="flex justify-between mt-8">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Назад
          </button>
          <button
            onClick={nextStep}
            disabled={!answers[currentQuestion.id]}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {currentStep === questions.length - 1 ? 'Завершить' : 'Далее'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;
