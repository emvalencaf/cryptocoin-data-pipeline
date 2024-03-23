class CurrencyDataRatesModel:
    def __init__(self, id: str, symbol: str,
                 currencySymbol: str, type: str,
                 rateUsd: str):
        self.id = id
        self.symbol = symbol
        self.currencySymbol = currencySymbol
        self.type = type
        self.rateUsd = rateUsd

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "currencySymbol": self.currencySymbol,
            "type": self.type,
            "rateUsd": self.rateUsd,
        }