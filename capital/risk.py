
from typing import Literal
from .schemas import Signal, Action

def target_vol_position_size(confidence: float, asset_class: str, horizon: str) -> float:
    """
    Простая функция сайзинга: чем выше уверенность, тем больше размер,
    но с крышами по классу актива и горизонту.
    """
    # базовые крышки
    caps = {
        ("crypto", "intraday"): 1.2,
        ("crypto", "swing"): 1.6,
        ("crypto", "position"): 2.0,
        ("equity", "intraday"): 0.8,
        ("equity", "swing"): 1.2,
        ("equity", "position"): 1.5,
    }
    cap = caps.get((asset_class, horizon), 1.0)
    # шкалирование 0.3%..cap% NAV
    size = 0.3 + confidence * (cap - 0.3)
    return round(size, 2)

def sanitize_levels(action: Action, entry: float, tp1: float, tp2: float, stop: float):
    """
    Гарантирует корректность уровней: стоп не хуже входа, цели в верной стороне.
    """
    if action == "BUY":
        # цели должны быть >= entry, стоп < entry
        tp1 = max(tp1, entry * 1.001)
        tp2 = max(tp2, tp1 * 1.001)
        stop = min(stop, entry * 0.999)
    elif action == "SHORT":
        # цели должны быть <= entry, стоп > entry
        tp1 = min(tp1, entry * 0.999)
        tp2 = min(tp2, tp1 * 0.999)
        stop = max(stop, entry * 1.001)
    # для CLOSE/WAIT уровни оставим как есть — они не используются на исполнение
    return tp1, tp2, stop
