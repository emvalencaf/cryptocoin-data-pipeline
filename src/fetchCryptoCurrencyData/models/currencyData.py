class CurrencyDataModel:
    def __init__(self, id: str, rank: int, symbol: str,
                 name: str, supply: str,
                 maxSupply: str,
                 marketCapUsd: str,
                 volumeUsd24Hr: str,
                 priceUsd: str,
                 changePercent24Hr: str,
                 vwap24Hr: str,
                 explorer: str):
        self.id = id
        self.rank = rank
        self.symbol = symbol
        self.name = name
        self.supply = supply
        self.maxSupply = maxSupply
        self.marketCapUsd = marketCapUsd
        self.volumeUsd24Hr = volumeUsd24Hr
        self.priceUsd = priceUsd
        self.changePercent24Hr = changePercent24Hr
        self.vwap24Hr = vwap24Hr
        self.explorer = explorer
        
    def to_dict(self):
        return {
            "id": self.id,
            "rank": self.rank,
            "symbol": self.symbol,
            "name": self.name,
            "supply": self.supply,
            "maxSupply": self.maxSupply,
            "marketCapUsd": self.marketCapUsd,
            "volumeUsd24Hr": self.volumeUsd24Hr,
            "priceUsd": self.priceUsd,
            "changePercent24Hr": self.changePercent24Hr,
            "vwap24Hr": self.vwap24Hr,
            "explorer": self.explorer
        }