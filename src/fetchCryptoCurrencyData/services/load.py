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
    
    def _uploadJsonObject(self, data: any,
                         endpoint: str,
                         filename: str):
        json_data = json.dumps(data, indent=2)
        
        # get current date
        current_date = datetime.now()
        
        filename = f'{current_date.timestamp}-{filename}.json'
        
        keyS3 = f'{self._s3_zone}/JSON/{endpoint.capitalize()}/{current_date.year}/{current_date.month}/{current_date.day}/{filename}'
        
        try:
            self._repositories.s3.put_object(Body= json_data,
                                             Bucket=self._bucket_name,
                                             Key=keyS3)
        except Exception as err:
            print(f'Error: {err}')
    
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
           
