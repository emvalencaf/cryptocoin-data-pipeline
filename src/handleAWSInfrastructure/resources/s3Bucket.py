from aws_cdk import aws_s3 as s3
from aws_cdk import Stack

import os

from dotenv import load_dotenv

load_dotenv()

class CdkS3BucketResource:
    def __init__(self, cdk: Stack, id_resource: str = "",
                 bucket_name: str = "") -> None:
        self._stack = cdk
        self._build(id,
                   bucket_name)
    
    def _build(self, id_resource: str = "",
              bucket_name: str = ""):
        
        bucket_name = os.getenv("BUCKET_NAME") if not bucket_name else bucket_name
        
        bucket_id = f"CDK-{bucket_name}" if not id_resource else bucket_name
        
        self._bucket = s3.Bucket(self._stack,
                                bucket_id,
                                bucket_name=bucket_name)