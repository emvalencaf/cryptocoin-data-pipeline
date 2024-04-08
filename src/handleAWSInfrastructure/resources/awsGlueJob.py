from aws_cdk import Stack
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam

import os

class CdkAWSGlueJobResource:
    def __init__(self, cdk: Stack,
                 aws_glue_job_id: str,
                 aws_glue_job_name: str,
                 aws_glue_role: iam.Role,
                 aws_glue_commands: glue.CfnJob.JobCommandProperty,
                 aws_glue_job_description: str,
                 aws_glue_default_args: dict,
                 aws_glue_worker_type: str = str(os.getenv("AWS_GLUE_WORKER_TYPE", "G.1X")),
                 aws_glue_version: str = str(os.getenv("AWS_GLUE_VERSION","4.0")),
                 aws_glue_n_workers: int = int(os.getenv("AWS_GLUE_N_WORKERS", "1"))) -> None:
        self._cdk = cdk
        self._aws_glue_job_id = aws_glue_job_id
        self._aws_glue_job_name = aws_glue_job_name
        self._aws_glue_role = aws_glue_role
        self._aws_glue_commands = aws_glue_commands
        self._aws_glue_n_workers = aws_glue_n_workers
        self._aws_glue_version = aws_glue_version
        self._aws_glue_job_description = aws_glue_job_description
        self._aws_glue_worker_type = aws_glue_worker_type
        self._aws_glue_default_args = aws_glue_default_args
        
        self._build()

    @property
    def job(self):
        return self._job
    
    def _build(self):
        self._job = glue.CfnJob(self._cdk,
                                self._aws_glue_job_id,
                                role=self._aws_glue_role.role_arn,
                                command=self._aws_glue_commands,
                                name=self._aws_glue_job_name,
                                glue_version=self._aws_glue_version,
                                number_of_workers=self._aws_glue_n_workers,
                                description=self._aws_glue_job_description,
                                worker_type=self._aws_glue_worker_type,
                                default_arguments=self._aws_glue_default_args,
                                )