class CurrencyValueModel:
    def __init__(self, id: str, rateUsd: str, timestamp: int):
        self.currency_id = id
        self.rateUsd = rateUsd
        self.timestamp = timestamp