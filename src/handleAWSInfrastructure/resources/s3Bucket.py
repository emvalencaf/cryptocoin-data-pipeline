from aws_cdk import aws_s3 as s3
from aws_cdk import Stack
import aws_cdk as cdk


from dotenv import load_dotenv

load_dotenv()

class CdkS3BucketResource:
    def __init__(self, cdk: Stack,
                 id_resource: str,
                 bucket_name: str,
                 auto_delete_objects: bool = True,
                 event_bridge_enabled: bool = False,
                 removal_policy: bool = True,
                 ) -> None:
        self._cdk = cdk
        self._id_resource = id_resource
        self._bucket_name = bucket_name
        self._auto_delete_objects = auto_delete_objects
        self._removal_policy = removal_policy
        self._event_bridge_enabled = event_bridge_enabled
        self._build()
    
    @property
    def bucket(self):
        return self._bucket
    
    @property
    def artifact_id(self):
        return self._bucket.stack.artifact_id

    def _build(self):
        
        bucket_name = self._bucket_name
        
        bucket_id = self._bucket_name
        
        self._bucket = s3.Bucket(self._cdk,
                                 bucket_id,
                                 bucket_name=bucket_name,
                                 auto_delete_objects=self._auto_delete_objects,
                                 removal_policy=cdk.RemovalPolicy.DESTROY if self._removal_policy else cdk.RemovalPolicy.RETAIN,
                                 event_bridge_enabled=self._event_bridge_enabled,)