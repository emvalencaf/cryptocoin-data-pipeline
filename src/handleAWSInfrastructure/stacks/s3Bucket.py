from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct

import os

from dotenv import load_dotenv

load_dotenv()

class CdkS3BucketStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.build()
    
    def build(self):
        bucket_name = os.getenv("BUCKET_NAME")
        s3.Bucket(self,f"CDK-{bucket_name}",
                  bucket_name=bucket_name)