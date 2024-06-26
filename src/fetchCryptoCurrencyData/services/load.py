import asyncio
import os
import json
from datetime import datetime

# repositories
from repositories.s3 import S3Repository

# models
from models.loadRepository import LoadRepositoryModel


class LoadService:
    def __init__(self, s3Repository: S3Repository):
        self._repositories = LoadRepositoryModel(s3Repository=s3Repository)
        self._s3_zone = os.getenv("S3_ZONE")
        self._bucket_name = os.getenv("BUCKET_NAME")
        self._batch_size = int(os.getenv("BATCH_SIZE", 100))
        self._objects_uploaded:list[str] = []
    
    @property
    def objects_uploaded(self):
        return tuple(uploaded for uploaded in self._objects_uploaded)
    
    def _add_object_uploaded(self, object_key: str):
        self._objects_uploaded.append(object_key)
    
    def _uploadJsonObject(self, data: any,
                         endpoint: str,
                         filename: str):
        json_data = json.dumps(data, indent=2)
        
        # get current date
        current_date = datetime.now()
        
        filename = f'{current_date.timestamp()}-{filename}.json'
        
        month = str(current_date.month).zfill(2)
        day = str(current_date.day).zfill(2)
        
        date_dir = f'{current_date.year}/{month}/{day}'
        
        keyS3 = f'{self._s3_zone}/JSON/{endpoint.capitalize()}/{date_dir}/{filename}'
            
        try:
            self._repositories.s3.put_object(Body= json_data,
                                             Bucket=self._bucket_name,
                                             Key=keyS3)
            # save in load service witches objects were uploaded
            self._add_object_uploaded(f'{endpoint.capitalize()}/{date_dir}/{filename}')
            
        except self._repositories.s3.exceptions.ClientError as err:
            print(err)
            raise err
    
    async def _uploadBatch(self, batch: any,
                           filename: str, endpoint: str):
        await asyncio.to_thread(self._uploadJsonObject, data=batch,
                                endpoint=endpoint, filename= filename)
    
    async def loadBatch(self, data: list, endpoint: str):
        print(f"Starting to load data from {endpoint} into {self._bucket_name}'s bucket at {self._s3_zone} zone it may take some time...")

        data = [el.to_dict() for el in data]
        
        batches = [data[i:i + self._batch_size] for i in range(0,len(data), self._batch_size)]
        
        tasks = [self._uploadBatch(batch=batch, filename=f"batch_{batch_idx + 1}", endpoint=endpoint) for batch_idx, batch in enumerate(batches)]
        
        await asyncio.gather(*tasks)
        
        n_s3_objs = len(batches)
        
        msg = f'The data ({n_s3_objs} objects uploaded) was successfully loaded into {self._bucket_name} in {self._s3_zone}/{endpoint.capitalize()}'
        
        print(msg)
        
        return msg
           
