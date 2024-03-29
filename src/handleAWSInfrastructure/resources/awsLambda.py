from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import Duration, Size

import os

class CdkAWSLambdaResource:
    def __init__(self, cdk: Stack,
                 _awslambda_id: str,
                 _awslambda_name: str,
                 _awslambda_timeout: int,
                 _awslambda_memory_size: int,
                 _awslambda_code_path: str,
                 _awslambda_role: iam.Role,
                 _awslambda_envs: dict[str, any] = {},) -> None:
        
        self._build(cdk,
                    _awslambda_id= _awslambda_id,
                    _awslambda_code_path= _awslambda_code_path,
                    _awslambda_name=_awslambda_name,
                    _awslambda_envs= _awslambda_envs,
                    _awslambda_memory_size= _awslambda_memory_size,
                    _awslambda_role=_awslambda_role,
                    _awslambda_timeout=_awslambda_timeout)

    """def _getEventRule(self):
        custom_rule_name = os.getenv("AMAZON_EVENTBRIDGE_RULE_NAME")
        custom_rule_schedule = os.getenv("AMAZON_EVENTBRIDGE_SCHEDULE_EXPRESSION")
        custom_rule_desc = os.getenv("AMAZON_EVENTBRIDGE_DESCRIPTION")
        
        return CdkEventSchedule(self, "FetchCryptoCurrency-Lambda-ScheduleEvent",
                                      custom_rule_name=custom_rule_name,
                                      custom_rule_schedule=custom_rule_schedule,
                                      custom_rule_desc=custom_rule_desc)"""

    """def _getLambdaIAMRole(self):
        BUCKET_NAME = self._getAWSLambdaEnvVarsToRun()["BUCKET_NAME"]
        
        lambda_role = iam.Role(self, "CdkFetchCryptoCurrency-Lambda",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")])

        s3_put_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"arn:aws:s3:::{BUCKET_NAME}/*"]
        )
        
        lambda_role.add_to_policy(s3_put_policy)
        
        return lambda_role"""        
    
    # get the env vars necessaries to run the fetchCryptoCurrencyDataLambda function
    """def _getAWSLambdaEnvVarsToRun(self):
        API_URL = os.getenv("API_URL")
        BATCH_SIZE = os.getenv("BATCH_SIZE")
        S3_ZONE = os.getenv("S3_ZONE")
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        return {
            "API_URL": API_URL,
            "BATCH_SIZE": BATCH_SIZE,
            "S3_ZONE": S3_ZONE,
            "BUCKET_NAME": BUCKET_NAME
        }"""
    
    def _build(self, cdk: Stack,
               _awslambda_id: str,
               _awslambda_name: str,
               _awslambda_timeout: int,
               _awslambda_memory_size: int,
               _awslambda_code_path: str,
               _awslambda_envs: dict[str, any],
               _awslambda_role: iam.Role):
        # getting event schedule rule
        # eventRule = self._getEventRule()
        
        
        # set aws lambda function config
        lambda_timeout = 60 if not  _awslambda_timeout else _awslambda_timeout
        
        _memory_size = 256 if not _awslambda_memory_size else _awslambda_memory_size
        
        lambda_memory_size = Size.mebibytes(_memory_size).to_mebibytes()
        
        # set lambda role
        # lambda_role = self._getLambdaIAMRole()

        self.prediction_lambda = _lambda.DockerImageFunction(scope=cdk,
                                                             id=_awslambda_id,
                                                             function_name=_awslambda_name,
                                                             code=_lambda.DockerImageCode.from_image_asset(directory=_awslambda_code_path),
                                                             environment=_awslambda_envs,
                                                             timeout= Duration.seconds(lambda_timeout),
                                                             memory_size=lambda_memory_size,
                                                             role=_awslambda_role)
        
        # eventRule.eventRule.add_target(target=targets.LambdaFunction(self.prediction_lambda))