from repositories.s3 import S3Repository

class LoadRepositoryModel:
    def __init__(self, s3Repository: S3Repository):
        self._s3 = s3Repository.client
        
    @property
    def s3(self):
        return self._s3