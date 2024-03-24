from aws_cdk import Stack, Duration
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

import os

from dotenv import load_dotenv

load_dotenv()

class CdkFetchCryptoCurrencyDataLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.build()
    
    def build(self):
        
        # getting amazon eventbridge env variables
        schedule_expression = events.Schedule.expression(os.getenv("AMAZON_EVENTBRIDGE_SCHEDULE_EXPRESSION"))
        
        rule = events.Rule(self, os.getenv("AMAZON_EVENTBRIDGE_RULE_NAME"),
                           description=os.getenv("AMAZON_EVENTBRIDGE_DESCRIPTION"),
                           schedule=schedule_expression)
        
        # getting lambda env variables
        API_URL = os.getenv("API_URL")
        BATCH_SIZE = os.getenv("BATCH_SIZE")
        S3_ZONE = os.getenv("S3_ZONE")
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        
        self.prediction_lambda = _lambda.DockerImageFunction(scope=self,
                                                             id="FetchCryptoCurrencyDataLambda",
                                                             function_name="fetchCryptoCurrencyData",
                                                             code=_lambda.DockerImageCode.from_image_asset(directory="../fetchCryptoCurrencyData"),
                                                             environment={
                                                                 "API_URL": API_URL,
                                                                 "BATCH_SIZE": BATCH_SIZE,
                                                                 "S3_ZONE": S3_ZONE,
                                                                 "BUCKET_NAME": BUCKET_NAME,}
                                                             )
        
        rule.add_target(targets.LambdaFunction(self.prediction_lambda))