from services.extract import ExtractService
from services.load import LoadService
from services.transform import TransformService

class ETLServicesModel:
    def __init__(self, loadService: LoadService):
        self._extract = ExtractService
        self._transform = TransformService
        self._load = loadService
    
    @property
    def extract(self):
        return self._extract
    
    @property
    def transform(self):
        return self._transform
    
    @property
    def load(self):
        return self._load