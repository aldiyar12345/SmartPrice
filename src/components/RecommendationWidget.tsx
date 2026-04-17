import React, { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';

interface Category {
  id: number;
  name: string;
}

interface Feature {
  id: number;
  name: string;
}

interface RecommendationWidgetProps {
  onRecommend: (products: any[]) => void;
  onClear: () => void;
}

export const RecommendationWidget: React.FC<RecommendationWidgetProps> = ({ onRecommend, onClear }) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCatId, setSelectedCatId] = useState<number | null>(null);
  const [features, setFeatures] = useState<Feature[]>([]);
  const [weights, setWeights] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/categories/')
      .then(res => res.json())
      .then(data => {
        const list = Array.isArray(data) ? data : data.results || [];
        setCategories(list);
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedCatId) {
      fetch(`/api/categories/${selectedCatId}/features/`)
        .then(res => res.json())
        .then(data => {
          setFeatures(data);
          const initialWeights: Record<number, number> = {};
          data.forEach((f: Feature) => {
            initialWeights[f.id] = 5; // Default middle value
          });
          setWeights(initialWeights);
        })
        .catch(console.error);
    } else {
      setFeatures([]);
      setWeights({});
    }
  }, [selectedCatId]);

  const handleRecommend = () => {
    if (!selectedCatId) return;
    setLoading(true);
    fetch('/api/recommend/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category_id: selectedCatId,
        weights: weights
      })
    })
      .then(res => res.json())
      .then(data => {
        onRecommend(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  return (
    <div className="bg-gradient-to-br from-emerald-50 to-white border-[3px] border-emerald-300 p-5 rounded-3xl shadow-sm mb-6 relative overflow-hidden">
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-emerald-200 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
      
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-emerald-500 rounded-xl">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-800">Персональные рекомендации (AI)</h2>
          <p className="text-xs text-slate-500">Укажите, что для вас важнее всего</p>
        </div>
      </div>

      <div className="space-y-4 relative z-10">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">Выберите категорию:</label>
          <div className="flex flex-wrap gap-2">
            {categories.map(c => (
              <button
                key={c.id}
                onClick={() => { setSelectedCatId(c.id); onClear(); }}
                className={`px-4 py-2 rounded-xl border-2 text-sm transition font-medium ${selectedCatId === c.id ? 'bg-emerald-500 border-emerald-500 text-white shadow-md' : 'bg-white border-emerald-200 text-slate-600 hover:border-emerald-400'}`}
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>

        {features.length > 0 && selectedCatId && (
          <div className="pt-3 border-t border-emerald-100">
            <label className="block text-sm font-semibold text-slate-700 mb-3">Оцените важность характеристик:</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
              {features.map(f => (
                <div key={f.id} className="flex flex-col gap-1">
                  <div className="flex justify-between text-xs font-medium text-slate-600">
                    <span>{f.name}</span>
                    <span className="text-emerald-600 font-bold">{weights[f.id] || 5}/10</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={weights[f.id] || 5}
                    onChange={(e) => setWeights({ ...weights, [f.id]: parseInt(e.target.value) })}
                    className="w-full accent-emerald-500"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>Неважно</span>
                    <span>Очень важно</span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-5 flex gap-3">
              <button
                onClick={handleRecommend}
                disabled={loading}
                className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-xl shadow-lg transition disabled:opacity-50"
              >
                {loading ? 'Анализируем...' : 'Найти лучшее совпадение'}
              </button>
              <button
                onClick={() => { setSelectedCatId(null); onClear(); }}
                className="px-4 py-3 bg-white border-2 border-slate-200 text-slate-600 font-bold rounded-xl hover:bg-slate-50 transition"
              >
                Сбросить
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
