
# services
import asyncio
from services.load import LoadService

# models
from models.currencyData import CurrencyDataModel
from models.currencyDataExtracted import CurrencyDataExtractedModel
from models.currencyDataRateExtracted import CurrencyDataRateExtractedModel
from models.currencyDataRates import CurrencyDataRatesModel
from models.responseAPI import APICoinCapResponse
from models.etlServices import ETLServicesModel

import os

class ETLController:
    def __init__(self, loadService: LoadService):
        self._services = ETLServicesModel(loadService=loadService)
    
    def execute(self):
        print('Fetching data from the API, please wait a little...')
        dataset = self._extractData()
        print("Data was successfully fetched.")   
        
        print('Starting transforming fetched data, please wait a little...')
        dataset = self._transformData(dataset=dataset)
        print('Data was successfully transformed...')
        
        return {
            "success_msg": self._loadData(dataset=dataset),
            "data": {
                "bucket_name": os.getenv("BUCKET_NAME"),
                "zone": "Raw",
                "objects_uploaded": self._services.load.objects_uploaded},
        }
    
    def _extractData(self):
        return self._services.extract.getRealTimeData(), self._services.extract.getCurrencyRates()

    def _transformData(self, dataset: tuple[APICoinCapResponse[CurrencyDataModel], APICoinCapResponse[CurrencyDataRatesModel]]):
        currenciesData = self._services.transform.intoCurrencyDataExtracted(dataset=dataset[0])
        currenciesDataRate = self._services.transform.intoCurrencyDataRateExtracted(dataset=dataset[1])
        return currenciesData, currenciesDataRate
    
    def _loadData(self,dataset: tuple[list[CurrencyDataExtractedModel], list[CurrencyDataRateExtractedModel]]):
        msg = asyncio.run(self._services.load.loadBatch(data=dataset[0], endpoint='assets'))
        msg2 = asyncio.run(self._services.load.loadBatch(data=dataset[1], endpoint='rates'))
        return f'{msg}\n{msg2}'