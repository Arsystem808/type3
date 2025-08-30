
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from .schemas import Signal

def toy_backtest(signal: Signal, n_steps: int = 400, step_bp: float = 15.0, fee_bp: float = 2.0) -> Dict:
    """
    Игрушечный симулятор: случайный ход цены вокруг входа.
    step_bp — средняя величина шага в б.п.
    fee_bp — комиссия сделки (в обе стороны).
    Возвращает метрики и серию equity.
    """
    entry = signal.entry
    action = signal.action
    rng = np.random.default_rng(42)  # детерминированный для воспроизводимости
    steps = rng.normal(loc=0.0, scale=step_bp/10000.0, size=n_steps)
    price = entry + np.cumsum(np.insert(steps * entry, 0, 0.0))  # эволюция цены

    # правила выхода
    tp1, tp2 = signal.take_profit
    stop = signal.stop

    pnl = 0.0
    exit_price = None
    for i, p in enumerate(price):
        if action == "BUY":
            if p >= tp2:
                exit_price = tp2; break
            if p >= tp1:
                exit_price = tp1; break
            if p <= stop:
                exit_price = stop; break
        elif action == "SHORT":
            if p <= tp2:
                exit_price = tp2; break
            if p <= tp1:
                exit_price = tp1; break
            if p >= stop:
                exit_price = stop; break
        else:
            # WAIT/CLOSE — нет сделки
            exit_price = entry; break

    if action == "BUY":
        pnl = (exit_price - entry) / entry
    elif action == "SHORT":
        pnl = (entry - exit_price) / entry
    else:
        pnl = 0.0

    # учтем комиссию (round-trip)
    fees = fee_bp/10000.0 * (1 if action in ["BUY", "SHORT"] else 0)
    pnl_after_fees = pnl - fees

    equity = (1 + pnl_after_fees)
    return dict(
        steps=int(i),
        exit_price=float(exit_price),
        pnl=float(pnl_after_fees),
        equity=float(equity),
    )
