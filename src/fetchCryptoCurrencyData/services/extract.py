# repositories
from repositories.cryptocurrencyapi import CryptoCurrencyAPIRepository

class ExtractService:
    def getRealTimeData(self, asset: str = ""):
        return CryptoCurrencyAPIRepository.getRealTimeData(asset=asset)
    
    def getHistoricalData(self, asset: str = ""):
        return CryptoCurrencyAPIRepository.getHistoricalData(asset=asset)
    
    def getCurrencyRates(cls, asset: str = ""):
        return CryptoCurrencyAPIRepository.getCurrencyRates(asset=asset) 