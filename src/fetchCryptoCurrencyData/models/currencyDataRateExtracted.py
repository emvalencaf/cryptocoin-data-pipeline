from typing import Union
import numpy as np

# models
from models.currencyDataRates import CurrencyDataRatesModel

class CurrencyDataRateExtractedModel(CurrencyDataRatesModel):
    def __init__(self, id: str, symbol: str,
                 currencySymbol: str, type: str,
                 rateUsd: str, timestamp: int):
        super().__init__(id=id, symbol=symbol,
                       currencySymbol=currencySymbol,
                       type=type, rateUsd=rateUsd)
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "currencySymbol": self.currencySymbol,
            "type": self.type,
            "rateUsd": self.rateUsd,
            "timestamp": self.timestamp
        }