from aws_cdk import Stack, Duration, Size
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from constructs import Construct
from events.event_rule_schedule import CdkEventSchedule

from aws_cdk import aws_events as events

import os

from dotenv import load_dotenv

load_dotenv()

class CdkFetchCryptoCurrencyDataLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.build()
    
    def _getEventRule(self):
        custom_rule_name = os.getenv("AMAZON_EVENTBRIDGE_RULE_NAME")
        custom_rule_schedule = os.getenv("AMAZON_EVENTBRIDGE_SCHEDULE_EXPRESSION")
        custom_rule_desc = os.getenv("AMAZON_EVENTBRIDGE_DESCRIPTION")
        
        return CdkEventSchedule(self, "FetchCryptoCurrency-Lambda-ScheduleEvent",
                                      custom_rule_name=custom_rule_name,
                                      custom_rule_schedule=custom_rule_schedule,
                                      custom_rule_desc=custom_rule_desc)
    
    def _getLambdaIAMRole(self):
        
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
        
        return lambda_role        
    
    # get the env vars necessaries to run the fetchCryptoCurrencyDataLambda function
    def _getAWSLambdaEnvVarsToRun(self):
        API_URL = os.getenv("API_URL")
        BATCH_SIZE = os.getenv("BATCH_SIZE")
        S3_ZONE = os.getenv("S3_ZONE")
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        return {
            "API_URL": API_URL,
            "BATCH_SIZE": BATCH_SIZE,
            "S3_ZONE": S3_ZONE,
            "BUCKET_NAME": BUCKET_NAME
        }
    
    def build(self):
        # getting event schedule rule
        eventRule = self._getEventRule()
        
        
        # set aws lambda function config
        lambda_timeout = int(os.getenv("AWS_LAMBDA_TIMEOUT", "60"))
        lambda_memory_size = Size.mebibytes(int(os.getenv("AWS_LAMBDA_MEMORY_SIZE", "256"))).to_mebibytes()
        
        # set lambda role
        lambda_role = self._getLambdaIAMRole()
        
        self.prediction_lambda = _lambda.DockerImageFunction(scope=self,
                                                             id="FetchCryptoCurrencyDataLambda",
                                                             function_name="fetchCryptoCurrencyData",
                                                             code=_lambda.DockerImageCode.from_image_asset(directory="../fetchCryptoCurrencyData"),
                                                             environment=self._getAWSLambdaEnvVarsToRun(),
                                                             timeout= Duration.seconds(lambda_timeout),
                                                             memory_size=lambda_memory_size,
                                                             role=lambda_role)
        
        eventRule.eventRule.add_target(target=targets.LambdaFunction(self.prediction_lambda))