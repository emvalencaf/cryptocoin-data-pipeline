from aws.aws_client import AWSClient

class S3Repository:
    def __init__(self):
        self._client = AWSClient.getAWSSession().client("s3")
    
    @property
    def client(self):
        return self._client