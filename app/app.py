
import json
import sys, os
from dotenv import load_dotenv
load_dotenv()
# --- Import guard: ensure project root on sys.path even if launched from /app ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from datetime import datetime
from capintel.signal_engine import build_signal
from capintel.providers.polygon_client import get_last_price, PolygonError
from capintel.backtest import toy_backtest

st.set_page_config(page_title="CapIntel — Signals", page_icon="📈", layout="wide")

st.title("📈 CapIntel — Идеи для Crypto & Equities (MVP)")
st.caption("Формат: BUY / SHORT / CLOSE / WAIT + уровни входа/целей/стопа, confidence и сценарии.")

with st.sidebar:
    st.header("Параметры")
    asset_class = st.selectbox("Класс актива", ["crypto", "equity"], index=0)
    horizon = st.selectbox("Горизонт", ["intraday", "swing", "position"], index=1)
    ticker = st.text_input("Тикер", value="BTCUSDT" if asset_class=="crypto" else "AAPL")
    last_price = st.number_input("Текущая цена", min_value=0.0001, value=65000.0 if asset_class=="crypto" else 230.0, step=0.1, format="%.4f")
    if st.button("Подтянуть цену из Polygon", use_container_width=True):
        try:
            fetched = get_last_price(asset_class, ticker)
            last_price = float(fetched)
            st.success(f"Цена обновлена: {last_price:.4f}")
        except PolygonError as e:
            st.error(str(e))
    st.write("---")
    st.markdown("**Совет:** укажи фактическую цену; логика не раскрывается — только действия и уровни.")
    go = st.button("Сгенерировать сигнал", use_container_width=True)

if go:
    sig = build_signal(ticker, asset_class, horizon, last_price)

    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.subheader(f"{sig.ticker} · {sig.asset_class.upper()} · {sig.horizon}")
        st.markdown(f"### ➤ Действие: **{sig.action}**")
        st.markdown(
            f"""
            **Вход:** `{sig.entry}`  
            **Цели:** `TP1 {sig.take_profit[0]}` · `TP2 {sig.take_profit[1]}`  
            **Стоп:** `{sig.stop}`  
            **Уверенность:** `{int(sig.confidence*100)}%`  
            **Размер позиции:** `{sig.position_size_pct_nav}% NAV`  
            """
        )
        st.info(sig.narrative_ru)

        st.markdown("**Альтернативный план**")
        alt = sig.alternatives[0]
        st.markdown(
            f"- {alt.if_condition}: **{alt.action}** от `{alt.entry}` → TP1 `{alt.take_profit[0]}`, TP2 `{alt.take_profit[1]}`, стоп `{alt.stop}`"
        )

        st.caption(f"Сигнал создан: {sig.created_at.strftime('%Y-%m-%d %H:%M UTC')} · Истекает: {sig.expires_at.strftime('%Y-%m-%d %H:%M UTC')}")
        st.caption(sig.disclaimer)

    with col2:
        st.markdown("#### JSON")
        st.code(json.dumps(sig.as_dict(), default=str, ensure_ascii=False, indent=2), language="json")

        st.markdown("#### «Игрушечный» бэктест")
        if sig.action in ["BUY", "SHORT"]:
            res = toy_backtest(sig)
            st.metric("Симулированный PnL (после комиссий)", f"{res['pnl']*100:.2f}%")
            st.metric("Выход по цене", f"{res['exit_price']:.4f}")
            st.metric("Шагов до выхода", res["steps"])
        else:
            st.caption("Для WAIT/CLOSE сделок нет: бэктест не запускается.")

    st.divider()
    st.caption("Этот MVP не раскрывает индикаторы или фичи. Формат и уровни поддерживают автопроверки (стопы/цели).")

else:
    st.markdown("> Выбери параметры слева и нажми **Сгенерировать сигнал**.")
