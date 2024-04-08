
from aws_cdk import Stack
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from aws_cdk import aws_s3_deployment as s3_deploy
from aws_cdk import aws_glue as glue
from constructs import Construct

import os

# events
from events.event_rule_schedule import CdkEventSchedule

# resources
from resources.awsLambda import CdkAWSLambdaResource
from resources.s3Bucket import CdkS3BucketResource
from resources.awsGlueJob import CdkAWSGlueJobResource
from resources.awsGlueDatabase import CdkAWSGlueDatabaseResource
from resources.awsGlueCrawler import CdkAWSGlueCrawlerResource

from dotenv import load_dotenv

load_dotenv()

class CdkDataPipelineStack(Stack):
    def __init__(self, scope: Construct,
                 construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id,
                         **kwargs)
        self._build()
    
    
    def _build(self):
        # create bucket to store data ingest and processed
        bucket = CdkS3BucketResource(self,
                                     id_resource=f'CDK-{os.getenv("BUCKET_NAME")}',
                                     bucket_name=os.getenv("BUCKET_NAME"),
                                     auto_delete_objects=True,
                                     removal_policy=True)
        
        # set iam policy to put object into a specific bucket
        s3_put_policy = self._setPolicyStatement(actions=["s3:PutObject"],
                                                 resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/*"],
                                                 effect_is_allowed=True)
        
        # set iam policy to get object to a specific bucket
        s3_get_policy = self._setPolicyStatement(actions=["s3:GetObject"],
                                                 resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/*"],
                                                 effect_is_allowed=True)

        # set iam policy to put object into a specific bucket
        s3_put_processing_data_policy = self._setPolicyStatement(actions=["s3:PutObject"],
                                                                 resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/Trusted/*"],
                                                                 effect_is_allowed=True)
        
        # set iam policy to get object to a specific bucket and zone
        s3_get_processing_data_policy = self._setPolicyStatement(actions=["s3:GetObject"],
                                                                 resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/Raw/*",
                                                                            f"arn:aws:s3:::{bucket._bucket.bucket_name}/Code/Glue_Job/ProcessingData/*"],
                                                                 effect_is_allowed=True)
        
        # set iam policy to put object into a specific bucket and zone
        s3_put_refining_data_policy = self._setPolicyStatement(actions=["s3:PutObject"],
                                                               resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/Refined/*"],
                                                               effect_is_allowed=True)
        
        # set iam policy to get object to a specific bucket and zone
        s3_get_refining_data_policy = self._setPolicyStatement(actions=["s3:GetObject"],
                                                               resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/Trusted/*",
                                                                          f"arn:aws:s3:::{bucket._bucket.bucket_name}/Refined/*",
                                                                          f"arn:aws:s3:::{bucket._bucket.bucket_name}/Code/Glue_Job/RefiningData/*"],
                                                               effect_is_allowed=True)
        # set iam policy to database
        aws_glue_database_policy = self._setPolicyStatement(actions=["glue:CreateDatabase",
                                                                     "glue:GetDatabase",
                                                                     "glue:UpdateDatabase",
                                                                     "glue:DeleteDatabase",
                                                                     "glue:GetTableVersions",
                                                                     "glue:GetTables",
                                                                     "glue:BatchCreatePartition",
                                                                     "glue:BatchDeletePartition",
                                                                     "glue:UpdateTable",
                                                                     "glue:BatchDeleteTableVersion",
                                                                     "lakeformation:GetDataAccess",
                                                                     "lakeformation:GrantPermissions",
                                                                     "lakeformation:RevokePermissions",
                                                                     "lakeformation:PutDataLakeSettings",
                                                                     "lakeformation:GetDataLakeSettings",
                                                                     ],
                                                            resources=["*"],
                                                            effect_is_allowed=True)
        
        # set iam role to database
        role_aws_glue_database = self._setIAMRole(role_id="Database-CryptoCurrency-Glue",
                                                  role_description="A Role for manager Database in AWS Glue",
                                                  role_service_principal="glue.amazonaws.com",
                                                  role_managed_policies="service-role/AWSGlueServiceRole",
                                                  role_policy_statements=[aws_glue_database_policy])
        
        # create database
        database = CdkAWSGlueDatabaseResource(cdk=self,
                                              database_id=os.getenv("AWS_GLUE_DATABASE_ID"),
                                              database_name=os.getenv("AWS_GLUE_DATABASE_NAME"),
                                              database_description=os.getenv("AWS_GLUE_DATABASE_DESCRIPTION"),
                                              aws_glue_role=role_aws_glue_database)
        
        # set iam policy to manage database
        aws_crawler_database_policy = self._setPolicyStatement(actions=["glue:CreateDatabase",
                                                                        "glue:GetTables",
                                                                        "glue:CreateTable",
                                                                        "glue:BatchCreatePartition",
                                                                        "glue:BatchDeletePartition",
                                                                        "glue:UpdateTable",],
                                                               resources=["*"],
                                                               effect_is_allowed=True)
        
        aws_crawler_s3_read_policy = self._setPolicyStatement(actions=["s3:getObject"],
                                                              resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/Refined/*"],
                                                              effect_is_allowed=True)
        
        aws_crawler_s3_put_policy = self._setPolicyStatement(actions=["s3:putObject"],
                                                             resources=["*"],
                                                             effect_is_allowed=True)
        
        aws_crawler_s3_list_bucket_policy = self._setPolicyStatement(actions=["s3:ListBucket"],
                                                                     resources=["*"],
                                                                     effect_is_allowed=True)
        
        # set iam role to fetchCryptoCurrency lambda function
        role_fetchCryptoCurrencyData = self._setIAMRole(role_id="CdkFetchCryptoCurrency-Lambda",
                                                        role_description=f"Role for Fetch Crypto Currency lambda function to fetch crypto currency data from an API and stores into /Raw zone within {bucket.bucket.bucket_name}",
                                                        role_service_principal="lambda.amazonaws.com",
                                                        role_managed_policies="service-role/AWSLambdaBasicExecutionRole",
                                                        role_policy_statements=[s3_put_policy])
        
        # set iam role to glue jobs
        role_glue_processing = self._setIAMRole(role_id="CdkJobProcessingData-Glue",
                                                role_description=f"A Role for AWS Glue job Processing Crypto Currency Data that will threat the stored data in /Raw zone within {bucket.bucket.bucket_name} and stored the threated data into /Trusted zone",
                                                role_service_principal="glue.amazonaws.com",
                                                role_managed_policies="service-role/AWSGlueServiceRole",
                                                role_policy_statements=[s3_get_processing_data_policy,
                                                                        s3_put_processing_data_policy])
        
        role_glue_refining = self._setIAMRole(role_id="CdkJobRefiningData-Glue",
                                              role_description=f"A Role for AWS Glue job Refining Crypto Currency Data stored at /Trusted zone within {bucket.bucket.bucket_name} and stored the refined data into /Refined zone",
                                              role_service_principal="glue.amazonaws.com",
                                              role_managed_policies="service-role/AWSGlueServiceRole",
                                              role_policy_statements=[s3_get_refining_data_policy,
                                                                      s3_put_refining_data_policy])
        
        # set iam role to GlueingCryptoCurrency crawler
        role_glueingCryptoCurrencyDataCrawler = self._setIAMRole(role_id="CdkCrawlerData-Glue",
                                                                 role_description=f"A Role for AWS Glue Crawler create and populate database tables by scraping /Refined zone within {bucket.bucket.bucket_name}",
                                                                 role_service_principal="glue.amazonaws.com",
                                                                 role_managed_policies="service-role/AWSGlueServiceRole",
                                                                 role_policy_statements=[aws_crawler_database_policy,
                                                                                         aws_crawler_s3_list_bucket_policy,
                                                                                         aws_crawler_s3_read_policy,
                                                                                         aws_crawler_s3_put_policy,])
        
        # set iam role to GlueingCryptoCurrency Step functions
        role_glueingCryptoCurrencyDataSfn = self._setIAMRole(role_id="CdkStepFunctions-Sfn",
                                                             role_description="A Role for AWS Step Function automate the data pipeline of crypto currency data by orchestrate AWS Lambda Function, AWS Glue Job and AWS Glue Crawler",
                                                             role_service_principal="states.amazonaws.com",
                                                             role_managed_policies="service-role/AWSLambdaBasicExecutionRole",
                                                             role_policy_statements=[s3_put_policy,
                                                                                      s3_get_policy])
        
        # set aws lambda envs
        fetchCryptoCurrencyData_envs = {
            "API_URL": os.getenv("API_URL"),
            "BATCH_SIZE": os.getenv("BATCH_SIZE"),
            "S3_ZONE": os.getenv("S3_ZONE"),
            "BUCKET_NAME": bucket._bucket.bucket_name}
        
        
        # config lambdas
        aws_lambda_config = {
            "aws_lambda_id":"FetchCryptoCurrencyData-LambdaFn",
            "aws_lambda_name":"fetchCryptoCurrencyData",
            "aws_lambda_timeout":int(os.getenv("FETCH_AWS_LAMBDA_TIMEOUT")),
            "aws_lambda_memory_size":int(os.getenv("FETCH_AWS_LAMBDA_MEMORY_SIZE")),
            "aws_lambda_code_path":"../fetchCryptoCurrencyData",
            "aws_lambda_envs": fetchCryptoCurrencyData_envs,
            "aws_lambda_role": role_fetchCryptoCurrencyData,
        }
        
        aws_lambda_fetch = CdkAWSLambdaResource(cdk=self, **aws_lambda_config)
        
        ibucket = bucket._bucket.from_bucket_arn(self,
                                                 id=bucket.artifact_id,
                                                 bucket_arn=bucket.bucket.bucket_arn)
        
        # deploy aws job code into s3
        s3_deploy.BucketDeployment(self, "DeployJob_TreatingData_Code",
                                   destination_bucket=ibucket,
                                   destination_key_prefix="Code/Glue_Job/ProcessingData",
                                   sources=[s3_deploy.Source.asset('../glueingCryptoCurrencyData/glueJobs/processingCryptoCurrencyData')],
                                   )
        
        s3_deploy.BucketDeployment(self, "DeployJob_RefiningData_Code",
                                   destination_bucket=ibucket,
                                   destination_key_prefix="Code/Glue_Job/RefiningData",
                                   sources=[s3_deploy.Source.asset('../glueingCryptoCurrencyData/glueJobs/refiningCryptoCurrencyData')],
                                   )
        
        # config glue job
        glue_treating_commands = glue.CfnJob.JobCommandProperty(name="glueetl",
                                                                python_version=os.getenv("AWS_GLUE_PYTHON_VERSION"),
                                                                script_location=f"s3://{bucket._bucket.bucket_name}/Code/Glue_Job/ProcessingData/main.py")
        
        glue_refining_commands = glue.CfnJob.JobCommandProperty(name="glueetl",
                                                                python_version=os.getenv("AWS_GLUE_PYTHON_VERSION"),
                                                                script_location=f"s3://{bucket._bucket.bucket_name}/Code/Glue_Job/RefiningData/main.py")
        
        glue_refining_args = {
            "--S3_BUCKET_NAME": bucket.bucket.bucket_name,
            "--S3_INPUT_ZONE": "Trusted",
            "--S3_TARGET_ZONE": "Refined",
            "--S3_ZONE_ENDPOINTS_DIR": "Assets,Rates",
            "--OBJECTS_KEY": ''
        }
        
        glue_treating_args = {
            "--S3_BUCKET_NAME": bucket.bucket.bucket_name,
            "--S3_INPUT_ZONE": "Raw",
            "--S3_TARGET_ZONE": "Trusted",
            "--S3_ZONE_ENDPOINTS_DIR": "Assets,Rates",
            "--OBJECTS_KEY": ''
        }
              
        aws_glue_job_configs = [
            {
                "aws_glue_job_id":"ProcessingCryptoCurrencyData-GlueJob",
                "aws_glue_job_name":"ProcessingCryptoCurrencyData-GlueJob",
                "aws_glue_role":role_glue_processing,
                "aws_glue_job_description": "A glue job to processing data stored in Raw zone converting string decimal into decimals and save files as parquet",
                "aws_glue_commands": glue_treating_commands,
                "aws_glue_default_args": glue_treating_args,
                }, {
                "aws_glue_job_id":"RefiningCryptoCurrencyData-GlueJob",
                "aws_glue_job_name":"RefiningCryptoCurrencyData-GlueJob",
                "aws_glue_role":role_glue_refining,
                "aws_glue_job_description": "A glue job to refining data stored in Trusted zone according to the database's business rule",
                "aws_glue_commands":glue_refining_commands,
                "aws_glue_default_args": glue_refining_args,
            }
        ]
        
        # creating glue jobs
        aws_glue_job_processing = CdkAWSGlueJobResource(cdk=self, **aws_glue_job_configs[0])
        aws_glue_job_refining = CdkAWSGlueJobResource(cdk=self, **aws_glue_job_configs[1])
        
        # set iam policy to assume role for step functions and also glueCryptoCurrencyData aws lambda
        sts_policy = self._setPolicyStatement(actions=["sts:AssumeRole"],
                                              resources=[role_glueingCryptoCurrencyDataSfn.role_arn,],
                                              effect_is_allowed=True)
        

        AWS_ACCOUNT = os.getenv("CDK_DEFAULT_ACCOUNT")
        AWS_REGION = os.getenv("CDK_DEFAULT_REGION")

        partial_arn_glue = f"arn:aws:glue:{AWS_REGION}:{AWS_ACCOUNT}:job/"

        glue_job_start_policy = self._setPolicyStatement(actions=["glue:StartJobRun"],
                                                         resources=[f'{partial_arn_glue}{aws_glue_job_processing.job.name}',
                                                                    f'{partial_arn_glue}{aws_glue_job_refining.job.name}'],
                                                         effect_is_allowed=True)
        
        lambda_invoke_policy = self._setPolicyStatement(actions=["lambda:InvokeFunction"],
                                                        resources=[aws_lambda_fetch.function_arn],
                                                        effect_is_allowed=True)
        
        # add invoke lambda policy to step functions
        role_glueingCryptoCurrencyDataSfn.add_to_policy(statement=sts_policy)
        role_glueingCryptoCurrencyDataSfn.add_to_policy(statement=lambda_invoke_policy)
        role_glueingCryptoCurrencyDataSfn.add_to_policy(statement=glue_job_start_policy)

        # create crawler
        aws_glue_crawler = CdkAWSGlueCrawlerResource(self,
                                                     aws_crawler_id="Crawler-CryptoCurrency",
                                                     aws_crawler_name="Crawler-CryptoCurrency",
                                                     aws_crawler_description=f"A crawler the data stored at /Refined zone to populate {database.database_name}",
                                                     aws_glue_role=role_glueingCryptoCurrencyDataCrawler,#role_glue_workflow,
                                                     database_name=database.database_name,
                                                     aws_glue_target={
                                                         "s3_path":f"s3://{bucket.bucket.bucket_name}/Refined",
                                                     })
        
        database.createPermission(id_permission=f"{aws_glue_crawler._id}-permission",
                                  role_arn=role_glueingCryptoCurrencyDataCrawler.role_arn,
                                  permissions=["ALL"])
        
        # create step functions
        self._buildMachineState(aws_lambda_fetch=aws_lambda_fetch,
                                aws_glue_job_processing=aws_glue_job_processing,
                                aws_glue_job_refining=aws_glue_job_refining,
                                aws_glue_crawler=aws_glue_crawler,
                                role=role_glueingCryptoCurrencyDataSfn)
        
    def _setIAMRole(self,
                    role_id: str,
                    role_description: str,
                    role_service_principal: str,
                    role_policy_statements: list[str],
                    role_managed_policies: str = "") -> iam.Role:
        _role = iam.Role(self,role_id,
                         description=role_description,
                         assumed_by=iam.ServicePrincipal(role_service_principal),)
        
        if role_managed_policies:
            _role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(role_managed_policies))
            
        for policy_statement in role_policy_statements:
            _role.add_to_policy(policy_statement)
        
        return _role
    
    def _setPolicyStatement(self,
                            actions: list[str],
                            resources: list[str],
                            effect_is_allowed: bool = True) -> iam.PolicyStatement:
        
        _policy_statement = iam.PolicyStatement(effect=iam.Effect.ALLOW if effect_is_allowed else iam.Effect.DENY,
                                                actions=actions,
                                                resources=resources,)
        
        return _policy_statement

    def _setStepJob(self, aws_job: CdkAWSGlueJobResource,
                    postfix: str = ""):
        
        s3_bucket_name = sfn.\
            JsonPath.\
            string_at("$.body.data.bucket_name") if postfix.lower() == "processing" else sfn.\
                JsonPath.string_at("$.Arguments.--S3_BUCKET_NAME")
                
        objects_key = sfn.\
            JsonPath.\
                string_at("$.body.data.objects_uploaded") if postfix.lower() == "processing" else sfn.\
                    JsonPath.string_at("$.Arguments.--OBJECTS_KEY")
        
        glue_job = sfn_tasks.GlueStartJobRun(self,
                                             f"{aws_job._aws_glue_job_name}-{postfix}",
                                             glue_job_name=aws_job.job.name,
                                             integration_pattern=sfn.IntegrationPattern.RUN_JOB,
                                             arguments=sfn.TaskInput.from_object({
                                                 "--S3_BUCKET_NAME": s3_bucket_name,
                                                 "--OBJECTS_KEY": objects_key,}))
        
        return glue_job
    
    def _setStepCrawlerRun(self,
                           aws_glue_crawler: CdkAWSGlueCrawlerResource,
                           postfix: str):
        glue_crawler = sfn_tasks.GlueStartCrawlerRun(self,
                                                     f"{aws_glue_crawler.crawler.name}-{postfix}",
                                                     crawler_name=aws_glue_crawler.crawler.name,
                                                     )
        
        return glue_crawler
        
    def _setStepLambda(self,
                 aws_lambda: CdkAWSLambdaResource,
                 postfix: str = ""):
        
        task_id = f"{aws_lambda.prediction_lambda.stack.artifact_id}-{postfix}" if postfix else aws_lambda.prediction_lambda.stack.artifact_id
        
        _lambda_fn = aws_lambda.prediction_lambda.from_function_arn(self,
                                                                     task_id,
                                                                     aws_lambda.function_arn)

        return sfn_tasks.LambdaInvoke(self,
                                      f"Invoke-{task_id}",
                                      lambda_function=_lambda_fn,
                                      output_path="$.Payload",)

    def _setDefineStateMachine(self,
                               aws_lambda_fetch: CdkAWSLambdaResource,
                               aws_glue_job_processing: CdkAWSGlueJobResource,
                               aws_glue_job_refining: CdkAWSGlueJobResource,
                               aws_glue_crawler: CdkAWSGlueCrawlerResource):
        
        step_1_ingesting = self._setStepLambda(aws_lambda=aws_lambda_fetch, postfix="Fetching")
        
        step_2_processing = self._setStepJob(aws_job=aws_glue_job_processing, postfix= "Processing")
        
        step_3_refining = self._setStepJob(aws_job=aws_glue_job_refining,
                                        postfix="Refining")
        
        step_4_crawling = self._setStepCrawlerRun(aws_glue_crawler=aws_glue_crawler,
                                                  postfix="Crawling")
        
        failure_state = sfn.Fail(self, "Fail")
        
        choice_steps = sfn.Choice(self, "IsFetchCrytoCurrencyDataSucceed?")
        choice_steps.when(sfn.Condition.number_equals("$.statusCode",
                                                       200),
                          step_2_processing)
        
        choice_steps.otherwise(failure_state)
        
        choice_step_3 = sfn.Choice(self, "IsRefiningCryptoCurrencyDataSucceed?")
        choice_step_3.when(sfn.Condition.string_equals("$.JobRunState",
                                                       "SUCCEEDED"),
                           step_4_crawling)
        
        choice_step_3.otherwise(failure_state)
        
        choice_step_2 = sfn.Choice(self, "IsProcessingCryptoCurrencyDataSucceed?")
        choice_step_2.when(sfn.Condition.string_equals("$.JobRunState",
                                                       "SUCCEEDED"),
                           step_3_refining)
        
        choice_step_2.otherwise(failure_state)
        
        # Define the state machine chain
        self._chain = sfn.Chain.start(step_1_ingesting).\
            next(choice_steps.afterwards()).\
                next(choice_step_2.afterwards()).\
                    next(choice_step_3)
        
    def _getEventRuleSchedule(self):
        custom_rule_name = os.getenv("AMAZON_EVENTBRIDGE_RULE_NAME")
        custom_rule_schedule = os.getenv("AMAZON_EVENTBRIDGE_SCHEDULE_EXPRESSION")
        custom_rule_desc = os.getenv("AMAZON_EVENTBRIDGE_DESCRIPTION")
        
        return CdkEventSchedule(self, "FetchCryptoCurrency-Lambda-ScheduleEvent",
                                      custom_rule_name=custom_rule_name,
                                      custom_rule_schedule=custom_rule_schedule,
                                      custom_rule_desc=custom_rule_desc)

    def _buildMachineState(self,
                           aws_lambda_fetch: CdkAWSLambdaResource,
                           aws_glue_job_processing: CdkAWSGlueJobResource,
                           aws_glue_job_refining: CdkAWSGlueJobResource,
                           aws_glue_crawler: CdkAWSGlueCrawlerResource,
                           role: iam.Role):
        eventRule = self._getEventRuleSchedule()
        
        self._setDefineStateMachine(aws_lambda_fetch=aws_lambda_fetch,
                                    aws_glue_job_processing=aws_glue_job_processing,
                                    aws_glue_job_refining=aws_glue_job_refining,
                                    aws_glue_crawler=aws_glue_crawler)
        
        definition_body = sfn.DefinitionBody.from_chainable(self._chain)
        
        self._stateMachine = sfn.StateMachine(self,
                                              'GlueingStateMachine',
                                              definition_body=definition_body,
                                              role=role)

        eventRule.eventRule.add_target(target=targets.SfnStateMachine(self._stateMachine))
       