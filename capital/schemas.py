
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
from datetime import datetime, timedelta

Action = Literal["BUY", "SHORT", "CLOSE", "WAIT"]
Horizon = Literal["intraday", "swing", "position"]
AssetClass = Literal["crypto", "equity"]

class SignalAlternative(BaseModel):
    if_condition: str = Field(..., description="Условие при котором активируется альтернативный сценарий")
    action: Action
    entry: float
    take_profit: List[float]
    stop: float

class Signal(BaseModel):
    id: str
    ticker: str
    asset_class: AssetClass
    horizon: Horizon
    action: Action
    entry: float
    take_profit: List[float] = Field(..., min_items=1, max_items=2)
    stop: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    position_size_pct_nav: float = Field(..., ge=0.0, le=100.0)
    created_at: datetime
    expires_at: datetime
    narrative_ru: str
    alternatives: List[SignalAlternative] = []
    disclaimer: str = "Не инвестиционный совет. Торговля сопряжена с риском."
    
    @validator("take_profit")
    def tp_sorted(cls, v):
        # Упорядочим цели по удаленности от входа
        return sorted(v, key=lambda x: x)

    @validator("stop")
    def stop_positive(cls, v):
        if v <= 0:
            raise ValueError("stop должен быть > 0")
        return v

    @validator("expires_at")
    def expires_after_created(cls, v, values):
        created = values.get("created_at")
        if created and v <= created:
            raise ValueError("expires_at должен быть позже created_at")
        return v

    def as_dict(self):
        return self.dict()
