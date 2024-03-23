from typing import Dict

# models
from models.currencyDataExtracted import CurrencyDataExtractedModel
from models.currencyData import CurrencyDataModel
from models.currencyDataRates import CurrencyDataRatesModel
from models.responseAPI import APICoinCapResponse
from models.currencyDataRateExtracted import CurrencyDataRateExtractedModel
from models.currencyValue import CurrencyValueModel

class TransformService:
    def intoCurrencyDataRateExtracted(self, dataset: APICoinCapResponse[CurrencyDataRatesModel]):
        return [CurrencyDataRateExtractedModel(**currency.to_dict(), timestamp=dataset.timestamp) for currency in dataset.data]
        
    def intoCurrencyDataExtracted(self, dataset: APICoinCapResponse[CurrencyDataModel]):
        return [CurrencyDataExtractedModel(**currency.to_dict(), timestamp=dataset.timestamp) for currency in dataset.data]