import sys

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col
from pyspark.sql.types import DecimalType
from pyspark.sql import DataFrame
import re

# @params: [JOB_NAME,
#           S3_BUCKET_NAME        || the S3 bucket where the objects were uploaded
#           S3_INPUT_ZONE         || the S3 bucket zone where the objects were uploaded
#           S3_TARGET_ZONE        || the S3 bucket zone where the processed data wil be uploaded
#           S3_ZONE_ENDPOINTS_DIR || The directories in bucket zone where the object were uploaded, ex.: ENDPOINT1, ENDPOINT2
#           OBJECTS_KEY           || The objects_key_prefix are a list of objects, ex: Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}
#           ]

args = getResolvedOptions(sys.argv, ['JOB_NAME',
                                     'S3_BUCKET_NAME',
                                     'S3_INPUT_ZONE',
                                     'S3_TARGET_ZONE',
                                     'S3_ZONE_ENDPOINTS_DIR',
                                     "OBJECTS_KEY"])

# initialize Spark app
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# getting bucket name
S3_BUCKET_NAME = str(args['S3_BUCKET_NAME'])

# getting the zone
S3_INPUT_ZONE = str(args['S3_INPUT_ZONE'])

# getting endpoints saved in Raw
ENDPOINTS = str(args['S3_ZONE_ENDPOINTS_DIR']).split(",")

# getting target zone
S3_TARGET_ZONE = str(args['S3_TARGET_ZONE'])

# utils functions
def getS3Path(prefix: str,
              endpoint: str,
              subdir:str = "",
              typeFile: str = "",
              filename:str = ""):
    
    endpoint = endpoint.lower().capitalize()
    
    filename = f'{subdir}/{filename}.{typeFile.lower()}' if subdir and typeFile and filename else ""
    
    return f"{prefix}/{endpoint}/{filename}"

def getTimestampFromKeyObject(object_key: str):
    
    timestamp_prefix = object_key.split("/")[-1].split("-")[0]
    
    return timestamp_prefix

def getDateSubDirFromKeyObject(object_key: str):
    regex_pattern_extract_subdir = r'(\d{4}/\d{2}/\d{2})'
    match = re.search(regex_pattern_extract_subdir, object_key)
    if match:
        return match.group()
    else:
        raise ValueError("No date subdirectory found in object key: {}".format(object_key))


# ETL functions
def extractData(prefix: str,
                endpoint: str,
                subdir: str = "",
                filename: str = "",
                typeFile: str = ""):
    
    objects_key = getS3Path(prefix=prefix,
                            endpoint=endpoint,
                            subdir=subdir,
                            filename=filename,
                            typeFile=typeFile)
    
    return spark.read.option("multiline","true").json(objects_key)


def transformData(endpoint: str,
                  df: DataFrame) -> DataFrame:
    if endpoint.lower() == "assets":
        cols_name = df.columns
        
        for col_name in cols_name:
            if col_name == 'marketCapUsd' or col_name == 'maxSupply' or col_name == 'priceUsd' or col_name == 'supply' or col_name == 'volumeUsd24Hr' or col_name == 'vwap24Hr':
                df = df.withColumn(col_name, col(col_name).cast(DecimalType(38, 18)))
                
        return df
    if endpoint.lower() == "rates":
        df = df.withColumn("rateUsd", col("rateUsd").cast(DecimalType(38, 18)))
        
        return df
    
    raise Exception("Invalid endpoint")

def loadData(prefix: str,
             endpoint: str,
             subdir_date: str,
             object_key: str,
             df: DataFrame) -> DataFrame:
    
    path = getS3Path(prefix=prefix,
                     endpoint=endpoint)
    
    df.write.parquet(f'{path}/{subdir_date}/{getTimestampFromKeyObject(object_key=object_key)}',
                     mode="overwrite")


def execute_job():
    extract_prefix = f"s3://{S3_BUCKET_NAME}/{S3_INPUT_ZONE}/JSON"
    
    load_prefix = f"s3://{S3_BUCKET_NAME}/{S3_TARGET_ZONE}"
    
    print(f"[GLUE_JOB_SYSTEM] - Starting to processing data from {extract_prefix} to store into {load_prefix}...")
    
    OBJECTS_KEY = str(args['OBJECTS_KEY'])
    objects_key = OBJECTS_KEY.split(",")
    for endpoint in ENDPOINTS:
        
        _objects_key = list(filter(lambda object_key: endpoint.lower().capitalize() in object_key,
                              objects_key))
        
        _str_objects_key = ", ".join(map(str, _objects_key))
        
        print(f"[GLUE_JOB_SYSTEM] - Starting processing data stores in {endpoint}...")
        print("[GLUE_JOB_SYSTEM] - The following files will be processed: {}".format(_str_objects_key))
        
        for object_key in _objects_key:
            print(f"[GLUE_JOB_SYSTEM] -  Starting extracting the data from {endpoint}...")
            
            subdir= getDateSubDirFromKeyObject(object_key=object_key)
            filename = f'{getTimestampFromKeyObject(object_key=object_key)}-*'
        
            df = extractData(prefix=extract_prefix,
                             endpoint=endpoint,
                             subdir=subdir,
                             filename=filename,
                             typeFile="json")
            
            print(f"[GLUE_JOB_SYSTEM] - The data extracted has the following scheme:")
            df.printSchema()
            
            print(f"[GLUE_JOB_SYSTEM] - Starting transforming the data from {endpoint}...")
            
            df = transformData(endpoint=endpoint,
                               df=df)
            
            print(f"[GLUE_JOB_SYSTEM] - The data transformed has the following scheme:")
            df.printSchema()
            
            print(f"[GLUE_JOB_SYSTEM] - Starting to load the transformed data into {load_prefix}...")

            loadData(prefix=load_prefix,
                     endpoint=endpoint,
                     subdir_date=subdir,
                     object_key=object_key,
                     df=df)

            print(f"[GLUE_JOB_SYSTEM] - The data was succefully loaded into {load_prefix}")
execute_job()
job.commit()