# controller
from controllers.etl import ETLController

# services
from services.load import LoadService

# repositories
from repositories.s3 import S3Repository

# instancing repositories
s3Repository = S3Repository()

# instancing services
loadService = LoadService(s3Repository=s3Repository)

# instancing the app
fetchCryptoCurrencyData = ETLController(loadService=loadService)