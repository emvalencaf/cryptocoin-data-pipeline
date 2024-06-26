

# models
from models.currencyData import CurrencyDataModel

class CurrencyDataExtractedModel(CurrencyDataModel):
    def __init__(self, id: str, rank: int, symbol: str,
                 name: str, supply: str,
                 maxSupply: str,
                 marketCapUsd: str,
                 volumeUsd24Hr: str,
                 priceUsd: str,
                 changePercent24Hr: str,
                 vwap24Hr: str, timestamp: int,
                 explorer: str):
        super().__init__(id=id, rank=rank,
                       symbol=symbol,name=name, supply=supply,
                       maxSupply=maxSupply, marketCapUsd=marketCapUsd,
                       volumeUsd24Hr=volumeUsd24Hr, priceUsd=priceUsd,
                       changePercent24Hr=changePercent24Hr,
                       vwap24Hr=vwap24Hr, explorer=explorer)
        self.timestamp=timestamp

    def to_dict(self):
        basedict = super().to_dict()
        basedict['timestamp'] = self.timestamp
        return basedict