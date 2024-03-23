from services.extract import ExtractService
from services.load import LoadService
from services.transform import TransformService

class ETLServicesModel:
    def __init__(self, extractService: ExtractService, transformService: TransformService, loadService: LoadService):
        self._extract = extractService
        self._transform = transformService
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