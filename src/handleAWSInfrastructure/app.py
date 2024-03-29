#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.dataPipeline import CdkDataPipelineStack

from dotenv import load_dotenv

load_dotenv()

app = cdk.App()

CdkDataPipelineStack(app, "Cdk-CryptoCurrencyData-DataPipeline",
                     env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                    region=os.getenv('CDK_DEFAULT_REGION')))

app.synth()
