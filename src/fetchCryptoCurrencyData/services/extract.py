# repositories
from repositories.cryptocurrencyapi import CryptoCurrencyAPIRepository

class ExtractService:
    @classmethod
    def getRealTimeData(cls, asset: str = ""):
        return CryptoCurrencyAPIRepository.getRealTimeData(asset=asset)
    @classmethod
    def getHistoricalData(cls, asset: str, interval: str):
        return CryptoCurrencyAPIRepository.getHistoricalData(asset=asset, interval=interval)
    @classmethod
    def getCurrencyRates(cls, asset: str = ""):
        return CryptoCurrencyAPIRepository.getCurrencyRates(asset=asset) 