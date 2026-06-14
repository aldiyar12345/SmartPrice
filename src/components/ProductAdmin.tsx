import React, { useState, useEffect } from 'react';

export const ProductAdmin: React.FC = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [price, setPrice] = useState('');
  const [marketplace, setMarketplace] = useState('Kaspi');

  const fetchData = async () => {
    setLoading(true);
    try {
      const pRes = await fetch('/api/admin/products/');
      const cRes = await fetch('/api/admin/categories/');
      if (pRes.ok && cRes.ok) {
        setProducts(await pRes.json());
        setCategories(await cRes.json());
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // 1. Create product
      const pRes = await fetch('/api/admin/products/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, category_id: categoryId, tags: [], rating: 5.0 })
      });
      
      if (pRes.ok) {
        const newProduct = await pRes.json();
        // 2. Add offer
        if (price && marketplace) {
          await fetch('/api/admin/offers/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product: newProduct.id, marketplace, price: parseFloat(price), label: 'Новое предложение' })
          });
        }
        alert('Товар успешно добавлен!');
        setName(''); setPrice('');
        fetchData();
      } else {
        alert('Ошибка при добавлении товара.');
      }
    } catch (e) {
      alert('Сбой сети.');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Удалить товар?")) return;
    try {
      await fetch(`/api/admin/products/${id}/`, { method: 'DELETE' });
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="text-sm text-slate-500">Загрузка товаров...</div>;

  return (
    <div className="mt-8 pt-8 border-t-2 border-slate-200">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Управление товарами</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 bg-slate-50 p-6 rounded-2xl border border-slate-200">
          <h3 className="font-semibold text-lg mb-4">Добавить новый товар</h3>
          <form onSubmit={handleAddProduct} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Название товара</label>
              <input value={name} onChange={e => setName(e.target.value)} required className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="iPhone 15 Pro Max" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Категория</label>
              <select value={categoryId} onChange={e => setCategoryId(e.target.value)} required className="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="">Выберите категорию</option>
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="pt-2 border-t border-slate-200 mt-2">
              <label className="block text-xs font-medium text-emerald-600 mb-1">Начальное предложение (Цена)</label>
              <input value={price} onChange={e => setPrice(e.target.value)} type="number" required className="w-full border rounded-lg px-3 py-2 text-sm mb-2" placeholder="Например: 600000" />
              <select value={marketplace} onChange={e => setMarketplace(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="Kaspi">Kaspi</option>
                <option value="Sulpak">Sulpak</option>
                <option value="Technodom">Technodom</option>
              </select>
            </div>
            <button type="submit" className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700 transition">Сохранить товар</button>
          </form>
        </div>

        <div className="md:col-span-2">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">ID</th>
                  <th className="px-4 py-3 font-medium">Товар</th>
                  <th className="px-4 py-3 font-medium">Категория</th>
                  <th className="px-4 py-3 font-medium">Действия</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {products.map((p: any) => (
                  <tr key={p.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-500">#{p.id}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{p.name}</td>
                    <td className="px-4 py-3 text-slate-600">{p.category}</td>
                    <td className="px-4 py-3">
                      <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:text-red-700 font-medium text-xs">Удалить</button>
                    </td>
                  </tr>
                ))}
                {products.length === 0 && (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-500">Нет товаров</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
