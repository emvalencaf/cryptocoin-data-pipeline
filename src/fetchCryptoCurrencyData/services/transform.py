from typing import Dict

# models
from models.currencyDataExtracted import CurrencyDataExtractedModel
from models.currencyData import CurrencyDataModel
from models.currencyDataRates import CurrencyDataRatesModel
from models.responseAPI import APICoinCapResponse
from models.currencyDataRateExtracted import CurrencyDataRateExtractedModel


class TransformService:
    @classmethod
    def intoCurrencyDataRateExtracted(cls, dataset: APICoinCapResponse[CurrencyDataRatesModel]):
        return [CurrencyDataRateExtractedModel(**currency.to_dict(), timestamp=dataset.timestamp) for currency in dataset.data]
    @classmethod
    def intoCurrencyDataExtracted(cls, dataset: APICoinCapResponse[CurrencyDataModel]):
        return [CurrencyDataExtractedModel(**currency.to_dict(), timestamp=dataset.timestamp) for currency in dataset.data]