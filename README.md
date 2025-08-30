
# CapIntel — Signals MVP (Crypto & Equities)

Готовый «хедж-фонд-лайт» скелет: FastAPI + Streamlit, сигналы BUY/SHORT/CLOSE/WAIT с уровнями, confidence, сценариями и проверками корректности.

## 🚀 Что внутри
- **API (FastAPI)**: `/signal` — выдаёт сигнал в фиксированном формате; `/backtest` — игрушечная симуляция.
- **App (Streamlit)**: рендер карточки идеи (действие, уровни, сценарий), JSON, быстрый сим-бэктест.
- **Engine**: мок-логика генерации уровней с авто-проверками (стопы/цели), sizing по confidence.
- **Narrator**: «голос трейдера» без индикаторов и раскрытия логики.
- **Tests**: базовые проверки валидности уровней.

> Важно: никакой индикаторной лексики в клиентском тексте; только цена и действие.

## 🧩 Установка
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Запуск
API:
```bash
uvicorn api.main:app --reload
```

Приложение:
```bash
streamlit run app/app.py
```

## 🔌 Пример запроса
```bash
curl -X POST http://127.0.0.1:8000/signal \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","asset_class":"equity","horizon":"swing","last_price":230.0}'
```

## 🧪 Локальный тест
```bash
pytest -q
```

## 🛡️ Guard-rails
- Авто-санитизация уровней: стоп не «хуже» входа, цели в нужной стороне.
- Сайзинг ограничен крышами по классу актива/горизонту.
- Текст сигнала — короткий, человеческий, без индикаторов/фич.

## 📦 Куда развивать дальше
- Подключить реальные данные и цену (binance/alphavantage/…).
- Добавить meta-labeling, regime-фильтр, калибровку вероятностей.
- Реальный бэктест: комиссии, спред, импакт, задержки, частичный fill.
- Портфель: таргет-волатильность, риск-лимиты, TCA, отчёты.
```


## 🔑 Polygon.io интеграция
Укажи ключ в окружении (любой из переменных читается):
```
export POLYGON_API_KEY=pk_************************
# (или) POLYGON_KEY / API_KEY
```

В Streamlit есть кнопка **«Подтянуть цену из Polygon»**, а в API доступен эндпоинт:
```
GET /price?asset_class=equity&ticker=AAPL
GET /price?asset_class=crypto&ticker=BTCUSD
```
Эндпоинты Polygon, которые используются:
- **Stocks Last Trade**: `/v2/last/trade/{stocksTicker}`  
- **Crypto Last Trade**: `/v1/last/crypto/{from}/{to}`  
- **Aggregates v2** (fallback): `/v2/aggs/ticker/{ticker}/range/1/minute/{from}/{to}?sort=desc&limit=1`
