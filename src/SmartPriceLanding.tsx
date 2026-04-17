import React, { useMemo, useState } from "react";
import { Search, Zap, Heart, Menu, X } from "lucide-react";
import { RecommendationWidget } from "./components/RecommendationWidget";

type MarketplaceOffer = {
  marketplace: string;
  price: number;
  label?: string;
  url?: string; // добавили поле для ссылки
};

type Product = {
  id: number;
  name: string;
  category: string;
  tags: string[];
  rating: number;
  offers: MarketplaceOffer[]; // топ‑3 цены
  match_score?: number; // балл совпадения (из API рекомендаций)
};

// Удалены жестко заданные массивы PRODUCTS и CATEGORIES

// Массив категорий теперь загружается с сервера

// фильтры передаются как пропсы, чтобы компонент не пересоздавался каждый рендер
interface FiltersProps {
  search: string;
  setSearch: React.Dispatch<React.SetStateAction<string>>;
  minPrice: string;
  setMinPrice: React.Dispatch<React.SetStateAction<string>>;
  maxPrice: string;
  setMaxPrice: React.Dispatch<React.SetStateAction<string>>;
}

const Filters = React.memo<FiltersProps>(
  ({ search, setSearch, minPrice, setMinPrice, maxPrice, setMaxPrice }: FiltersProps) => (
    <section className="mb-6">
      <div className="bg-white border-2 border-emerald-500 rounded-2xl p-3 flex flex-col md:flex-row gap-3 md:items-center shadow-sm">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border-[3px] border-emerald-700 rounded-xl pl-9 pr-3 py-2 text-sm font-semibold text-slate-900 placeholder:text-slate-500 outline-none focus:border-emerald-900 focus:ring-1 focus:ring-emerald-300/70 transition"
            placeholder="Поиск товара: название, бренд, модель"
          />
        </div>
        <div className="flex gap-2">
          <input
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            className="w-24 bg-white border-[3px] border-emerald-700 rounded-xl px-2 py-2 text-xs font-semibold text-slate-900 placeholder:text-slate-500 outline-none focus:border-emerald-900 focus:ring-1 focus:ring-emerald-300/70 transition"
            placeholder="от"
          />
          <input
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            className="w-24 bg-white border-[3px] border-emerald-700 rounded-xl px-2 py-2 text-xs font-semibold text-slate-900 placeholder:text-slate-500 outline-none focus:border-emerald-900 focus:ring-1 focus:ring-emerald-300/70 transition"
            placeholder="до"
          />
        </div>
      </div>
    </section>
  )
);



type Page = "home" | "catalog" | "favorites" | "profile";

const SmartPriceLanding: React.FC = () => {
  const [page, setPage] = useState<Page>("home");
  const [menuOpen, setMenuOpen] = useState(false);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string>("Все категории");
  const [minPrice, setMinPrice] = useState<string>("");
  const [maxPrice, setMaxPrice] = useState<string>("");

  const [categories, setCategories] = useState<string[]>(["Все категории"]);
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendedProducts, setRecommendedProducts] = useState<Product[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);
  const [user, setUser] = useState<{ email: string } | null>(null);

  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const [pendingPass, setPendingPass] = useState<string | null>(null);
  const [sentCode, setSentCode] = useState<string | null>(null);
  const [codeInput, setCodeInput] = useState("");
  const [submissionId, setSubmissionId] = useState<number | null>(null);

  // AI Chat states
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{ role: "user" | "ai"; content: string; id: number }[]>([
    { id: 1, role: "ai", content: "Привет! Я умный помощник SmartPrice. О каком товаре вы хотите узнать?" }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isTyping) return;
    const userMsg = chatInput;
    setChatInput("");
    setChatMessages(prev => [...prev, { id: Date.now(), role: "user", content: userMsg }]);
    setIsTyping(true);

    try {
      const resp = await fetch("/api/chat/query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await resp.json();
      setChatMessages(prev => [...prev, { id: Date.now() + 1, role: "ai", content: data.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { id: Date.now() + 1, role: "ai", content: "Простите, произошла ошибка подключения." }]);
    } finally {
      setIsTyping(false);
    }
  };


  // Загрузка категорий один раз при старте
  React.useEffect(() => {
    fetch("/api/categories/")
      .then(res => res.json())
      .then(data => {
        const list = Array.isArray(data) ? data : (data && Array.isArray(data.results) ? data.results : null);
        if (list) {
          const names = list.map((c: any) => c.name);
          setCategories(["Все категории", ...names]);
        }
      })
      .catch(err => console.error("Error fetching categories:", err));
  }, []);

  // Загрузка товаров при изменении фильтров
  React.useEffect(() => {
    setLoading(true);
    setRecommendedProducts(null);
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category !== "Все категории") params.append("category", category);
    if (minPrice) params.append("min_price", minPrice.replace(/\s/g, ""));
    if (maxPrice) params.append("max_price", maxPrice.replace(/\s/g, ""));

    fetch(`/api/products/?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        // API возвращает список товаров. Если нужно ограничить избранным на клиенте:
        // API может возвращать либо массив, либо объект с полем results (пагинация)
        let list = Array.isArray(data) ? data : (data && Array.isArray(data.results) ? data.results : []);
        if (page === "favorites") {
          list = list.filter((p: Product) => p && favoriteIds.includes(p.id));
        }
        setProducts(list);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching products:", err);
        setLoading(false);
      });
  }, [search, category, minPrice, maxPrice, page, favoriteIds]);

  // читаем сохранённого пользователя из localStorage при загрузке
  React.useEffect(() => {
    const stored = localStorage.getItem("sp_user");
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch { }
    }
  }, []);

  const saveUser = (u: { email: string } | null) => {
    setUser(u);
    if (u) {
      localStorage.setItem("sp_user", JSON.stringify(u));
    } else {
      localStorage.removeItem("sp_user");
      // при выходе сбрасываем проверочные данные
      setSentCode(null);
      setPendingEmail(null);
      setPendingPass(null);
      setSubmissionId(null);
      setCodeInput("");
    }
  };

  const toggleFavorite = (id: number) => {
    setFavoriteIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  // helper that computes filtered products based on current filters
  // Теперь фильтрация происходит преимущественно на бэкенде,
  // результаты уже в состоянии `products`.
  const displayedProducts = products;

  const renderProducts = (products: Product[]) => {
    if (!products.length) {
      return (
        <div className="text-sm text-slate-500 border-2 border-dashed border-emerald-200 rounded-2xl p-6 text-center bg-white/80">
          Не нашли подходящих товаров по текущим фильтрам.
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {products.map((p) => (
          <article
            key={p.id}
            className="bg-white border-[3px] border-emerald-500 rounded-2xl p-4 flex flex-col gap-3 shadow-sm hover:border-emerald-600 hover:shadow-[0_18px_40px_rgba(16,185,129,0.2)] transition"
          >
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-slate-900 mb-1">
                  {p.name}
                </h3>
                <div className="flex items-center gap-2 text-[11px] text-slate-500">
                  <span>{p.category}</span>
                  <span className="h-1 w-1 rounded-full bg-slate-600" />
                  <span>Рейтинг {Number(p.rating || 0).toFixed(1)}</span>
                  {p.match_score !== undefined && (
                     <>
                       <span className="h-1 w-1 rounded-full bg-emerald-500" />
                       <span className="text-emerald-700 font-bold bg-emerald-100 px-1.5 py-0.5 rounded-md">Балл ИИ: {p.match_score.toFixed(0)}</span>
                     </>
                  )}
                </div>
              </div>
              <button
                type="button"
                aria-label="Избранное"
                onClick={() => toggleFavorite(p.id)}
                className="p-1 -mr-1 transition"
              >
                <Heart
                  className="w-4 h-4"
                  color={favoriteIds.includes(p.id) ? "#ef4444" : "#94a3b8"}
                  fill={favoriteIds.includes(p.id) ? "#ef4444" : "none"}
                />
              </button>
            </div>

            <div className="border-t border-emerald-200 pt-3 mt-1">
              <div className="text-[11px] uppercase tracking-wide text-emerald-700 mb-2">
                Топ‑3 предложения
              </div>
              <div className="space-y-1.5 text-xs text-slate-800">
                {(p.offers || []).map((o) => (
                  <div
                    key={o.marketplace}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      {o.url ? (
                        <a
                          href={o.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-0.5 rounded-full bg-emerald-50 text-[11px] text-emerald-700 border border-emerald-100 hover:bg-emerald-100 transition inline-block"
                        >
                          {o.marketplace}
                        </a>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-[11px] text-emerald-700 border border-emerald-100">
                          {o.marketplace}
                        </span>
                      )}
                      {o.label && (
                        <span className="text-[11px] text-emerald-400">
                          {o.label}
                        </span>
                      )}
                    </div>
                    <span className="text-slate-900 font-semibold">
                      {(o.price || 0).toLocaleString("ru-RU")} ₸
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
    );
  };



  return (
    <>
      <style>{`
        :root {
          --bg-primary: #ffffff;
          --accent-from: #77dd77;
          --accent-to: #5fbf5f;
          --accent-secondary: #86efac;
          --soft-lime: #E2FFAD;
          --soft-lime-hover: #DFFF00;
        }

        html {
          scroll-behavior: smooth;
        }

        body {
          background: #ffffff;
        }

        .gradient-text {
          background-image: linear-gradient(120deg, var(--accent-from), var(--accent-to), var(--accent-secondary));
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }

        .nav-blur {
          background: rgba(255,255,255,0.96);
          backdrop-filter: blur(18px);
        }
      `}</style>

      <div className="min-h-screen flex flex-col bg-[radial-gradient(circle_at_top,_#e5ffe5,_#ffffff_50%,_#e0f2f1_100%)] text-slate-900 antialiased">
        <header className="fixed inset-x-0 top-0 z-40 nav-blur border-b border-emerald-100">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <button
              type="button"
              className="flex items-center gap-2"
              onClick={() => {
                setPage("home");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
            >
              <div className="h-9 w-9 rounded-2xl bg-gradient-to-tr from-[#77dd77] via-[#5fbf5f] to-emerald-600 flex items-center justify-center shadow-[0_0_22px_rgba(119,221,119,0.8)]">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div className="flex flex-col leading-tight text-left">
                <span className="text-lg font-semibold tracking-tight">
                  SmartPrice
                </span>
                <span className="text-[11px] text-slate-500">
                  AI Price Navigator
                </span>
              </div>
            </button>

            <nav className="hidden md:flex items-center gap-3 text-sm text-slate-700">
              {/* Добавляем кнопку профиля справа */}
              <button
                type="button"
                onClick={() => {
                  setPage("home");
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className={`px-4 py-2 rounded-xl border-2 text-sm font-medium transition ${page === "home"
                  ? "border-[var(--soft-lime)] bg-[var(--soft-lime)] text-slate-900 shadow-[0_0_22px_rgba(226,255,173,0.7)]"
                  : "border-slate-300 bg-white text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900"
                  }`}
              >
                Главная
              </button>
              <button
                type="button"
                onClick={() => {
                  setPage("catalog");
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className={`px-4 py-2 rounded-xl border-2 text-sm font-medium transition ${page === "catalog"
                  ? "border-[var(--soft-lime)] bg-[var(--soft-lime)] text-slate-900 shadow-[0_0_22px_rgba(226,255,173,0.7)]"
                  : "border-slate-300 bg-white text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900"
                  }`}
              >
                Каталог
              </button>
              <button
                type="button"
                onClick={() => {
                  setPage("favorites");
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className={`px-4 py-2 rounded-xl border-2 text-sm font-medium inline-flex items-center gap-1 transition ${page === "favorites"
                  ? "border-[var(--soft-lime)] bg-[var(--soft-lime)] text-slate-900 shadow-[0_0_22px_rgba(226,255,173,0.7)]"
                  : "border-slate-300 bg-white text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900"
                  }`}
              >
                <Heart className="w-3.5 h-3.5" />
                Избранное
              </button>
              <button
                type="button"
                onClick={() => {
                  setPage("profile");
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className={`px-4 py-2 rounded-xl border-2 text-sm font-medium transition ${page === "profile"
                  ? "border-[var(--soft-lime)] bg-[var(--soft-lime)] text-slate-900 shadow-[0_0_22px_rgba(226,255,173,0.7)]"
                  : "border-slate-300 bg-white text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900"
                  }`}
              >
                {user ? user.email : "Профиль"}
              </button>
            </nav>

            <button
              type="button"
              className="md:hidden inline-flex items-center justify-center h-8 w-8 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-200"
              onClick={() => setMenuOpen((v) => !v)}
            >
              {menuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
            {/* мобильная кнопка профиля */}
            <button
              type="button"
              className="md:hidden ml-2 inline-flex items-center justify-center h-8 w-8 rounded-xl border-2 border-slate-300 bg-white text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900 transition"
              onClick={() => setPage("profile")}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A9 9 0 0112 15a9 9 0 016.879 2.804M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </button>
          </div>

          {menuOpen && (
            <div className="md:hidden border-t border-slate-800/80 bg-slate-950/95">
              <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col gap-2 text-sm text-slate-700">
                <button
                  type="button"
                  className="px-4 py-2 rounded-xl border-2 border-[var(--soft-lime)] bg-[var(--soft-lime)] text-left text-sm font-medium text-slate-900 hover:brightness-105 transition"
                  onClick={() => {
                    setPage("home");
                    setMenuOpen(false);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  Главная
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-xl border-2 border-slate-300 bg-white text-left text-sm font-medium text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900 transition"
                  onClick={() => {
                    setPage("catalog");
                    setMenuOpen(false);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  Каталог
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-xl border-2 border-slate-300 bg-white text-left text-sm font-medium inline-flex items-center gap-1 text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900 transition"
                  onClick={() => {
                    setPage("favorites");
                    setMenuOpen(false);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  <Heart className="w-3.5 h-3.5" />
                  Избранные товары
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-xl border-2 border-slate-300 bg-white text-left text-sm font-medium text-slate-800 hover:bg-[var(--soft-lime)] hover:text-slate-900 transition"
                  onClick={() => {
                    setPage("profile");
                    setMenuOpen(false);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  {user ? user.email : "Профиль"}
                </button>
              </div>
            </div>
          )}
        </header>

        <main className="flex-1 pt-16">
          <div className="max-w-6xl mx-auto px-4 py-10 space-y-6">
            {page === "home" && (
              <>
                <section className="space-y-3">
                  <p className="text-xs sm:text-sm font-semibold tracking-wide text-emerald-700 bg-emerald-50 inline-flex px-3 py-1 rounded-full border border-emerald-200 mb-1">
                    Умный поиск
                  </p>
                  <h1 className="text-3xl sm:text-4xl font-semibold text-slate-900">
                    Находи лучшую цену за секунды
                  </h1>
                  <p className="text-sm text-slate-700 max-w-xl">
                    Один запрос — и SmartPrice сравнивает цены и условия на Sulpak,
                    Technodom, Lamoda, AliExpress, Wildberries, Ozon и других
                    маркетплейсах.
                  </p>
                </section>
                <Filters
                  search={search}
                  setSearch={setSearch}
                  minPrice={minPrice}
                  setMinPrice={setMinPrice}
                  maxPrice={maxPrice}
                  setMaxPrice={setMaxPrice}
                />
                {renderProducts(displayedProducts)}
              </>
            )}

            {page === "catalog" && (
              <>
                <section className="space-y-2 mb-6">
                  <h1 className="text-2xl sm:text-3xl font-semibold text-slate-800">
                    Каталог товаров
                  </h1>
                  <p className="text-sm text-slate-500 max-w-xl">
                    Все категории и товары в одном месте. Вы можете воспользоваться умным подбором от ИИ, 
                    чтобы найти то, что идеально вам подходит!
                  </p>
                </section>
                
                <RecommendationWidget 
                  onRecommend={(prods) => setRecommendedProducts(prods)}
                  onClear={() => setRecommendedProducts(null)}
                />

                {!recommendedProducts && (
                  <>
                    <Filters
                      search={search}
                      setSearch={setSearch}
                      minPrice={minPrice}
                      setMinPrice={setMinPrice}
                      maxPrice={maxPrice}
                      setMaxPrice={setMaxPrice}
                    />
                    <section className="mb-4">
                      <h2 className="text-xs uppercase tracking-wide text-slate-500 mb-2">
                        Категории ({categories.length})
                      </h2>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                        {categories.map((c) => {
                          const isActive = c === category;
                          return (
                            <button
                              key={c}
                              type="button"
                              onClick={() => setCategory(c)}
                              className={`w-full text-left px-4 py-2 rounded-2xl border text-slate-900 transition ${isActive
                                ? "bg-[var(--soft-lime-hover)] border-[#A8D89F]"
                                : "bg-[var(--soft-lime)] border-[#C0E8A1] hover:bg-[var(--soft-lime-hover)]/80"
                                }`}
                            >
                              {c}
                            </button>
                          );
                        })}
                      </div>
                    </section>
                  </>
                )}

                {recommendedProducts && (
                  <div className="mb-4 text-emerald-800 font-bold bg-emerald-100 border-2 border-emerald-300 p-3 rounded-xl flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    Топ совпадений: от самых подходящих к наименее
                  </div>
                )}

                {renderProducts(recommendedProducts || displayedProducts)}
              </>
            )}

            {page === "favorites" && (
              <>
                <section className="space-y-2">
                  <h1 className="text-2xl sm:text-3xl font-semibold text-slate-50">
                    Избранные товары
                  </h1>
                  <p className="text-sm text-slate-500 max-w-xl">
                    Список товаров, которые вы пометили как избранные. Следите за
                    лучшими ценами и не теряйте важные позиции.
                  </p>
                </section>
                <Filters
                  search={search}
                  setSearch={setSearch}
                  minPrice={minPrice}
                  setMinPrice={setMinPrice}
                  maxPrice={maxPrice}
                  setMaxPrice={setMaxPrice}
                />
                {renderProducts(displayedProducts)}
              </>
            )}

            {page === "profile" && (
              <section className="max-w-md mx-auto bg-white p-6 rounded-2xl shadow-md">
                {!user ? (
                  !sentCode ? (
                    <>
                      <h2 className="text-xl font-semibold mb-4">Войти или зарегистрироваться</h2>
                      <form
                        onSubmit={async (e) => {
                          e.preventDefault();
                          const form = e.target as HTMLFormElement;
                          const email = (form.elements.namedItem("email") as HTMLInputElement).value;
                          const password = (form.elements.namedItem("password") as HTMLInputElement).value;

                          try {
                            const response = await fetch("/api/auth/submit/", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({ email, password }),
                            });

                            if (response.ok) {
                              const data = await response.json();
                              setSubmissionId(data.id);
                              setSentCode(data.code);
                              setPendingEmail(email);
                              alert(`Код подтверждения: ${data.code}`);
                            } else {
                              const err = await response.json();
                              alert(err.error || "Ошибка при отправке данных");
                            }
                          } catch (error) {
                            alert("Не удалось связаться с сервером. Убедитесь, что backend запущен.");
                          }
                        }}
                      >
                        <div className="mb-3">
                          <label className="block text-sm font-medium mb-1" htmlFor="email">
                            Email
                          </label>
                          <input
                            id="email"
                            name="email"
                            type="email"
                            required
                            className="w-full border-2 border-slate-300 rounded-xl px-3 py-2 outline-none focus:border-[var(--soft-lime)] focus:ring-1 focus:ring-[var(--soft-lime-hover)]/70"
                            placeholder="you@example.com"
                          />
                        </div>
                        <div className="mb-4">
                          <label className="block text-sm font-medium mb-1" htmlFor="password">
                            Пароль
                          </label>
                          <input
                            id="password"
                            name="password"
                            type="password"
                            required
                            className="w-full border-2 border-slate-300 rounded-xl px-3 py-2 outline-none focus:border-[var(--soft-lime)] focus:ring-1 focus:ring-[var(--soft-lime-hover)]/70"
                          />
                        </div>
                        <button
                          type="submit"
                          className="w-full py-2 rounded-xl bg-[var(--soft-lime)] text-slate-900 font-semibold hover:bg-[var(--soft-lime-hover)] transition"
                        >
                          Войти / Зарегистрироваться
                        </button>
                      </form>
                      <p className="text-xs text-slate-500 mt-3">
                        Введите почту и пароль в поля выше и нажмите кнопку. В коде
                        обработчик формы (onSubmit) читает эти значения, смотрите
                        комментарии.
                      </p>
                    </>
                  ) : (
                    /* отображаем поле ввода 6‑значного кода */
                    <>
                      <h2 className="text-xl font-semibold mb-4">Проверка кода</h2>
                      <p className="text-sm text-slate-500 mb-4">
                        Код выслан в терминал. Введите его здесь:
                      </p>
                      <div className="mb-3">
                        <input
                          value={codeInput}
                          onChange={(e) => setCodeInput(e.target.value)}
                          className="w-full border-2 border-slate-300 rounded-xl px-3 py-2 outline-none focus:border-[var(--soft-lime)] focus:ring-1 focus:ring-[var(--soft-lime-hover)]/70"
                          placeholder="123456"
                        />
                      </div>
                      <button
                        type="button"
                        className="w-full py-2 rounded-xl bg-[var(--soft-lime)] text-slate-900 font-semibold hover:bg-[var(--soft-lime-hover)] transition"
                        onClick={async () => {
                          if (!submissionId) return;

                          try {
                            const response = await fetch("/api/auth/verify/", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({ id: submissionId, code: codeInput }),
                            });

                            if (response.ok) {
                              saveUser({ email: pendingEmail! });
                              setSentCode(null);
                              setPendingEmail(null);
                              setSubmissionId(null);
                              setCodeInput("");
                            } else {
                              const err = await response.json();
                              alert(err.error || "Неверный код, попробуйте ещё раз");
                            }
                          } catch (error) {
                            alert("Ошибка верификации");
                          }
                        }}
                      >
                        Подтвердить
                      </button>
                      <p className="text-xs text-slate-500 mt-3">
                        Этот код выводится в консоль (в терминал сборщика). Поищите
                        сообщение "verification code".
                      </p>
                    </>
                  )
                ) : (
                  <>
                    <h2 className="text-xl font-semibold mb-4">Привет, {user.email}</h2>
                    <p className="mb-4 text-sm text-slate-600">
                      Это ваш профиль. Здесь будет отображаться корзина и история заказов.
                    </p>
                    <button
                      type="button"
                      onClick={() => saveUser(null)}
                      className="mb-4 py-2 px-4 rounded-xl bg-red-200 text-red-800 hover:bg-red-300 transition"
                    >
                      Выйти
                    </button>
                    <div className="border-t pt-4">
                      <h3 className="font-medium mb-2">Корзина (пока пусто)</h3>
                    </div>
                  </>
                )}
              </section>
            )}
          </div>
        </main>

        <footer className="border-t border-slate-800/80 bg-slate-950/95 mt-4">
          <div className="max-w-6xl mx-auto px-4 py-8">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500">
              <span>
                © {new Date().getFullYear()} SmartPrice AI. Все права защищены.
              </span>
              <span>Фокус на скорость, экономию и прозрачность цен.</span>
            </div>
          </div>
        </footer>

        {/* Floating AI Chat Widget */}
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
          {chatOpen && (
            <div className="w-[320px] sm:w-[380px] h-[450px] bg-white rounded-3xl shadow-2xl border-2 border-emerald-500 flex flex-col overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
              {/* Header */}
              <div className="bg-emerald-600 p-4 text-white flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="bg-white/20 p-1.5 rounded-xl">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold">AI Assistant</h3>
                    <p className="text-[10px] text-emerald-100">SmartPrice Navigator</p>
                  </div>
                </div>
                <button onClick={() => setChatOpen(false)} className="hover:bg-white/20 p-1.5 rounded-xl transition">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
                {chatMessages.map((m) => (
                  <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm ${m.role === "user"
                        ? "bg-emerald-600 text-white rounded-tr-none shadow-md"
                        : "bg-white text-slate-800 rounded-tl-none border border-slate-200 shadow-sm"
                      }`}>
                      {m.content.split("**").map((part, i) => i % 2 === 1 ? <strong key={i}>{part}</strong> : part)}
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-white px-4 py-2 rounded-2xl rounded-tl-none border border-slate-100 shadow-sm">
                      <div className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce"></span>
                        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                        <span className="w-1.5 h-1.5 bg-emerald-600 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <form
                onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                className="p-3 bg-white border-t border-slate-100 flex gap-2 items-center"
              >
                <input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Спросите о товаре..."
                  className="flex-1 bg-slate-100 border-none rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none transition"
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim() || isTyping}
                  className="bg-emerald-600 text-white p-2 rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition shadow-lg"
                >
                  <Zap className="w-4 h-4 fill-white" />
                </button>
              </form>
            </div>
          )}

          <button
            onClick={() => setChatOpen(!chatOpen)}
            className={`h-14 w-14 rounded-2xl flex items-center justify-center shadow-2xl transition-all duration-300 transform hover:scale-105 active:scale-95 ${chatOpen ? "bg-slate-800 text-white rotate-90" : "bg-emerald-600 text-white"
              }`}
          >
            {chatOpen ? <X className="w-6 h-6" /> : <Zap className="w-6 h-6 fill-white" />}
            {!chatOpen && chatMessages.length === 1 && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border-2 border-white"></span>
              </span>
            )}
          </button>
        </div>
      </div>
    </>
  );
};

export default SmartPriceLanding;

