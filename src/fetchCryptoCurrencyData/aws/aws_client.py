import boto3

class AWSClient:
    @classmethod
    def getAWSSession(cls):      
        return boto3.session.Session()