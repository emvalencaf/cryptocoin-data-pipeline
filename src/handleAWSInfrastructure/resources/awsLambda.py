from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import Duration, Size

import os

class CdkAWSLambdaResource:
    def __init__(self, cdk: Stack,
                 aws_lambda_id: str,
                 aws_lambda_name: str,
                 aws_lambda_code_path: str,
                 aws_lambda_role: iam.Role,
                 aws_lambda_memory_size: int = int(os.getenv("AWS_LAMBDA_MEMORY_SIZE", "512")),
                 aws_lambda_timeout: int = int(os.getenv("AWS_LAMBDA_TIMEOUT", "60")),
                 aws_lambda_envs: dict[str, any] = {},) -> None:
        self._cdk = cdk
        self._aws_lambda_id = aws_lambda_id
        self._aws_lambda_name = aws_lambda_name
        self._aws_lambda_code_path = aws_lambda_code_path
        self._aws_lambda_envs = aws_lambda_envs
        self._aws_lambda_role = aws_lambda_role
        self._aws_lambda_memory_size = aws_lambda_memory_size
        self._aws_lambda_timeout = aws_lambda_timeout
        self._build()
        
    @property
    def function_name(self):
        return self.prediction_lambda.function_name
    
    @property
    def function_arn(self):
        return self.prediction_lambda.function_arn
    
    @property
    def artifact_id(self):
        return self.prediction_lambda.stack.artifact_id
    
    def _build(self):
        
        # set aws lambda function config
        lambda_timeout = self._aws_lambda_timeout
        
        _memory_size = self._aws_lambda_memory_size
        
        lambda_memory_size = Size.mebibytes(_memory_size).to_mebibytes()

        self.prediction_lambda = _lambda.DockerImageFunction(scope=self._cdk,
                                                             id=self._aws_lambda_id,
                                                             function_name=self._aws_lambda_name,
                                                             code=_lambda.DockerImageCode.from_image_asset(directory=self._aws_lambda_code_path),
                                                             environment=self._aws_lambda_envs,
                                                             timeout= Duration.seconds(lambda_timeout),
                                                             memory_size=lambda_memory_size,
                                                             role=self._aws_lambda_role)