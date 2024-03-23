# controller
from controllers.etl import ETLController

# services
from services.extract import ExtractService
from services.load import LoadService
from services.transform import TransformService

# repositories
from repositories.s3 import S3Repository

# instancing repositories
s3Repository = S3Repository()

# instancing services
loadService = LoadService(s3Repository=s3Repository)
extractService = ExtractService()
transformService = TransformService()

# instancing the app
fetchCryptoCurrencyData = ETLController(extractService=extractService,
                                        loadService=loadService,
                                        transformService=transformService)