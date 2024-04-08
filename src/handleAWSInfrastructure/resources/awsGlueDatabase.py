from aws_cdk import Stack
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lakeformation as lakeformation

import os

class CdkAWSGlueDatabaseResource:
    def __init__(self, cdk: Stack,
                 database_id:str,
                 database_name: str,
                 database_description: str,
                 aws_glue_role: iam.Role,):
        self._cdk = cdk
        self._database_id = database_id
        self._database_name = database_name.lower()
        self._database_description = database_description
        self._aws_glue_role = aws_glue_role

        self._build()
        
    @property
    def database_name(self):
        return self._database_name
    
    def _createDB(self):
        database_input = glue.CfnDatabase.DatabaseInputProperty(name=self._database_name,
                                                                description=self._database_description)
        
        return glue.CfnDatabase(self._cdk,
                                id=self._database_id,
                                catalog_id=os.getenv("CDK_DEFAULT_ACCOUNT"),
                                database_input=database_input,)
    """   
    def _setPermissions(self):
        resource = lakeformation.CfnPermissions.ResourceProperty(
              database_resource=lakeformation.CfnPermissions.DatabaseResourceProperty(
                  catalog_id=self._db.catalog_id,
                  name=self._database_name))
        data_lake_principal = lakeformation.CfnPermissions.\
                              DataLakePrincipalProperty(
                                    data_lake_principal_identifier=self._aws_glue_role.role_arn,
                                    resource=resource)
        return lakeformation.\
               CfnPermissions(self._cdk,
                              id=f'{self._database_id}-permissions',
                              data_lake_principal=data_lake_principal,
                              permissions=['ALL'])
    """
    
    def createPermission(self,
                         id_permission: str,
                         role_arn: str,
                         permissions: list[str]):
        database_resource = lakeformation.\
                                CfnPermissions.\
                                    DatabaseResourceProperty(catalog_id=self._db.catalog_id,
                                                             name=self._database_name)
        
        resource = lakeformation.\
                        CfnPermissions.\
                            ResourceProperty(database_resource=database_resource,)
                
        data_lake_principal = lakeformation.\
            CfnPermissions.\
                DataLakePrincipalProperty(data_lake_principal_identifier=role_arn)
        
        return lakeformation.CfnPermissions(self._cdk,
                                            id=id_permission,
                                            data_lake_principal=data_lake_principal,
                                            resource=resource,
                                            permissions=permissions)
        
    def _build(self):
        self._db = self._createDB()
        # self._lake_permissions = self._setPermissions()
        self.createPermission(id_permission=f"{self._database_name}-permissions",
                              role_arn=self._aws_glue_role.role_arn,
                              permissions=['ALL'])