from typing import TypedDict


class CurrencyDataHistoricalModel(TypedDict):
    def __init__(self, time: int, priceUsd: str):
        self.time = time
        self.priceUsd = priceUsd
    