
from aws_cdk import Stack
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from constructs import Construct
from events.event_rule_schedule import CdkEventSchedule

from aws_cdk import aws_events as events

import os

# resources
from resources.awsLambda import CdkAWSLambdaResource
from resources.s3Bucket import CdkS3BucketResource

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
        bucket = CdkS3BucketResource(self)
        
        # set iam policy to put object into a specific bucket
        s3_put_policy = self._setPolicyStatement(_actions=["s3:PutObject"],
                                                  _resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/*"],
                                                  _effect_is_allowed=True)
        
        # set iam policy to get object to a specific bucket
        s3_get_policy = self._setPolicyStatement(_actions=["s3:GetObject"],
                                                  _resources=[f"arn:aws:s3:::{bucket._bucket.bucket_name}/*"],
                                                  _effect_is_allowed=True)
        
        # set iam role to fetchCryptoCurrency lambda function
        role_fetchCryptoCurrencyData = self._setIAMRole(_role_id="CdkFetchCryptoCurrency-Lambda",
                                                        _role_service_principal="lambda.amazonaws.com",
                                                        _role_managed_policies="service-role/AWSLambdaBasicExecutionRole",
                                                        _role_policy_statements=[s3_put_policy])
        
        # set iam role to glueingCryptoCurrencyData lambda function
        role_glueingCryptoCurrencyData = self._setIAMRole(_role_id="CdkGlueingCryptoCurrencyData-Lambda",
                                                        _role_service_principal="lambda.amazonaws.com",
                                                        _role_managed_policies="service-role/AWSLambdaBasicExecutionRole",
                                                        _role_policy_statements=[s3_put_policy, s3_get_policy])
        
        role_glueingCryptoCurrencyDataSfn = self._setIAMRole(_role_id="CdkStepFunctions-Sfn",
                                                        _role_service_principal="states.amazonaws.com",
                                                        _role_managed_policies="service-role/AWSLambdaBasicExecutionRole",
                                                        _role_policy_statements=[s3_put_policy, s3_get_policy])
        
        # set aws lambda envs
        fetchCryptoCurrencyData_envs = {
            "API_URL": os.getenv("API_URL"),
            "BATCH_SIZE": os.getenv("BATCH_SIZE"),
            "S3_ZONE": os.getenv("S3_ZONE"),
            "BUCKET_NAME": bucket._bucket.bucket_name}
        
        
        # config lambdas
        
        aws_lambdas_config = [{
                "_awslambda_id":"FetchCryptoCurrencyData-LambdaFn",
                "_awslambda_name":"fetchCryptoCurrencyData",
                "_awslambda_timeout":int(os.getenv("FETCH_AWS_LAMBDA_TIMEOUT")),
                "_awslambda_memory_size":int(os.getenv("FETCH_AWS_LAMBDA_MEMORY_SIZE")),
                "_awslambda_code_path":"../fetchCryptoCurrencyData",
                "_awslambda_envs": fetchCryptoCurrencyData_envs,
                "_awslambda_role": role_fetchCryptoCurrencyData,
            },{
                "_awslambda_id":"GlueingCryptoCurrencyData-LambdaFn",
                "_awslambda_name":"glueingCryptoCurrencyData",
                "_awslambda_timeout":int(os.getenv("TRANSFORM_AWS_LAMBDA_TIMEOUT")),
                "_awslambda_memory_size":int(os.getenv("TRANSFORM_AWS_LAMBDA_MEMORY_SIZE")),
                "_awslambda_code_path":"../glueingCryptoCurrencyData",
                "_awslambda_role": role_glueingCryptoCurrencyData,
            }]
        
        # create lambda functions
        aws_lambda_fns: tuple[_lambda.DockerImageFunction] = tuple([CdkAWSLambdaResource(cdk=self, **aws_lambda_config).prediction_lambda for aws_lambda_config in aws_lambdas_config])
        
        # set iam policy to assume role
        sts_policy = self._setPolicyStatement(_actions=["sts:AssumeRole"],
                                              _resources=[role_glueingCryptoCurrencyDataSfn.role_arn],
                                              _effect_is_allowed=True)
        

        AWS_ACCOUNT = os.getenv("CDK_DEFAULT_ACCOUNT")
        AWS_REGION = os.getenv("CDK_DEFAULT_reGION")

        partial_arn = f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT}:function:"
        
        lambda_invoke_policy = self._setPolicyStatement(_actions=["lambda:InvokeFunction"],
                                                        _resources=[f"{partial_arn}{aws_lambda.function_name}" for aws_lambda in aws_lambda_fns],
                                                        _effect_is_allowed=True)
        
        role_glueingCryptoCurrencyDataSfn.add_to_policy(statement=sts_policy)
        role_glueingCryptoCurrencyDataSfn.add_to_policy(statement=lambda_invoke_policy)

        # create step functions
        self._buildMachineState(_aws_lambda_fns=aws_lambda_fns,
                                _role=role_glueingCryptoCurrencyDataSfn)
        
    def _setIAMRole(self,
                    _role_id: str,
                    _role_service_principal: str,
                    _role_managed_policies: str,
                    _role_policy_statements: list[str]) -> iam.Role:
        _role = iam.Role(self,_role_id,
                         assumed_by=iam.ServicePrincipal(_role_service_principal),
                         managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(_role_managed_policies)])
        
        for _policy_statement in _role_policy_statements:
            _role.add_to_policy(_policy_statement)
        
        return _role
    
    def _setPolicyStatement(self,
                            _actions: list[str],
                            _resources: list[str],
                            _effect_is_allowed: bool = True) -> iam.PolicyStatement:
        
        _policy_statement = iam.PolicyStatement(
            effect=iam.Effect.ALLOW if _effect_is_allowed else iam.Effect.DENY,
            actions=_actions,
            resources=_resources,
        )
        
        return _policy_statement


    def _setStep(self,
                 _aws_lambda: _lambda.DockerImageFunction,
                 postfix: str = ""):
        
        task_id = f"{_aws_lambda.stack.artifact_id}-{postfix}" if postfix else _aws_lambda.stack.artifact_id
        
        _lambda_fn = _aws_lambda.from_function_arn(self,
                                                   task_id,
                                                   _aws_lambda.function_arn)
        """"
        if "FetchCryptoCurrencyData" in _lambda_fn.function_name:
            return sfn_tasks.LambdaInvoke(self,
                                          f"Invoke-{task_id}",
                                          lambda_function=_lambda_fn,
                                          output_path="$.Payload")"""

        return sfn_tasks.LambdaInvoke(self,
                                      f"Invoke-{task_id}",
                                      lambda_function=_lambda_fn,
                                      output_path="$.Payload",)
    
    def _setDefineStateMachine(self,
                               _aws_lambda_fns: tuple[_lambda.DockerImageFunction]):
        
        step_1_ingesting = self._setStep(_aws_lambda=_aws_lambda_fns[0])
        
        step_2_processing = self._setStep(_aws_lambda=_aws_lambda_fns[1],
                                          postfix="Processing")
        
        step_3_refining = self._setStep(_aws_lambda=_aws_lambda_fns[1],
                                        postfix="Refining")
        
        failure_state = sfn.Fail(self, "Fail")
        
        choice_step_2 = sfn.Choice(self, "IsGlueingCryptoCurrencyDataSucceed?")
        choice_step_2.when(sfn.Condition.number_equals("$.statusCode",
                                                       200), step_3_refining)
        choice_step_2.otherwise(failure_state)
        
        choice_steps = sfn.Choice(self, "IsFetchCrytoCurrencyDataSucceed?")
        choice_steps.when(sfn.Condition.number_equals("$.statusCode",
                                                       200), step_2_processing)
        choice_steps.otherwise(failure_state)
        # Define the state machine chain
        self._chain = sfn.Chain.start(step_1_ingesting).next(choice_steps)
    
    def _getEventRule(self):
        custom_rule_name = os.getenv("AMAZON_EVENTBRIDGE_RULE_NAME")
        custom_rule_schedule = os.getenv("AMAZON_EVENTBRIDGE_SCHEDULE_EXPRESSION")
        custom_rule_desc = os.getenv("AMAZON_EVENTBRIDGE_DESCRIPTION")
        
        return CdkEventSchedule(self, "FetchCryptoCurrency-Lambda-ScheduleEvent",
                                      custom_rule_name=custom_rule_name,
                                      custom_rule_schedule=custom_rule_schedule,
                                      custom_rule_desc=custom_rule_desc)
        
    def _buildMachineState(self,
                           _aws_lambda_fns: tuple[_lambda.DockerImageFunction],
                           _role: iam.Role):
        eventRule = self._getEventRule()
        
        self._setDefineStateMachine(_aws_lambda_fns=_aws_lambda_fns)
        
        definition_body = sfn.DefinitionBody.from_chainable(self._chain)
        
        self._stateMachine = sfn.StateMachine(self,
                                              'GlueingStateMachine',
                                              definition_body=definition_body,
                                              role=_role)

        eventRule.eventRule.add_target(target=targets.SfnStateMachine(self._stateMachine))
        