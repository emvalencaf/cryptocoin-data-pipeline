from aws_cdk import Stack
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam

import os

class CdkAWSGlueCrawlerResource:
    def __init__(self, cdk: Stack,
                 aws_crawler_id: str,
                 aws_crawler_name: str,
                 aws_glue_role: iam.IRole,
                 database_name: str,
                 aws_crawler_description: str,
                 aws_glue_target: dict[str, any]):
        self._cdk = cdk
        self._id = aws_crawler_id
        self._crawler_name = aws_crawler_name
        self._crawler_description = aws_crawler_description
        self._aws_glue_role = aws_glue_role
        self._database_name = database_name
        self._aws_glue_target =aws_glue_target

        self._build()
        
    @property
    def crawler(self):
        return self._crawler
    
    def _build(self):
        
        s3_target = glue.CfnCrawler.S3TargetProperty(path=self._aws_glue_target["s3_path"])
        
        targets = glue.CfnCrawler.TargetsProperty(
            s3_targets=[s3_target]
        )
        
        # incremental crawler (to crawl only new data input)
        recrawl_policy= glue.CfnCrawler.RecrawlPolicyProperty(
                     recrawl_behavior='CRAWL_EVERYTHING')
        
        self._crawler = glue.CfnCrawler(self._cdk,
                                        id=self._id,
                                        name=self._crawler_name,
                                        description=self._crawler_description,
                                        role=self._aws_glue_role.role_arn,
                                        database_name=self._database_name,
                                        targets=targets,
                                        recrawl_policy=recrawl_policy)