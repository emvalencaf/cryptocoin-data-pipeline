#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.fetchCryptoCurrencyData import CdkFetchCryptoCurrencyDataLambdaStack
from stacks.s3Bucket import CdkS3BucketStack
from dotenv import load_dotenv

load_dotenv()

app = cdk.App()

CdkS3BucketStack(app, "Bucket",
                env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                    region=os.getenv('CDK_DEFAULT_REGION')))

CdkFetchCryptoCurrencyDataLambdaStack(app, "FetchCryptoCurrencyDataLambda",
                                      env=cdk.Environment(
                                          account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),)

app.synth()
