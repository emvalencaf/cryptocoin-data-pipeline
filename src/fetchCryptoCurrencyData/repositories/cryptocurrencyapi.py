import requests
import os

# models
from models.currencyDataRates import CurrencyDataRatesModel
from models.responseAPI import APICoinCapResponse
from models.currencyData import CurrencyDataModel
from models.currencyDataHistorical import CurrencyDataHistoricalModel

API_URL = os.getenv("API_URL")

class CryptoCurrencyAPIRepository:
    @classmethod
    def _fetchData(cls,endpoint: str) -> APICoinCapResponse:
        try:
            res = requests.get(API_URL + endpoint)
            
            if res.status_code == 200:
                return res.json()
            else:
                print(f'Error: {res.status_code} - {res.reason}')
        except requests.exceptions.RequestException as err:
            print(f'Error: {err}')
                
    @classmethod
    def getRealTimeData(cls, asset: str = "") -> APICoinCapResponse[CurrencyDataModel]:
        res = cls._fetchData(f'/assets/{asset}')
        return APICoinCapResponse(data=[CurrencyDataModel(**data_currency) for data_currency in res['data']],
                                  timestamp=res['timestamp'])
    
    @classmethod
    def getHistoricalData(cls, asset: str, interval: str):
        res = cls._fetchData(f'/assets/{asset}/history?interval={interval}')
        return APICoinCapResponse(data= [CurrencyDataHistoricalModel(**currency) for currency in res["data"]],
                                  timestamp=res['timestamp'])
    
    @classmethod
    def getCurrencyRates(cls, asset: str = "") -> APICoinCapResponse[CurrencyDataRatesModel]:
        res = cls._fetchData(f'/rates/{asset}')
        return APICoinCapResponse(data=[CurrencyDataRatesModel(**currency) for currency in res["data"]],
                                  timestamp=res['timestamp'])