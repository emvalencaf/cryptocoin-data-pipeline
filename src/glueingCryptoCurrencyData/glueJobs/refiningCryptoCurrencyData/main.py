import sys

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, substring
from pyspark.sql import DataFrame
import re

# @params: [JOB_NAME, S3_BUCKET_NAME, S3_INPUT_ZONE, S3_TARGET_ZONE, S3_ZONE_ENDPOINTS_DIR, OBJECTS_KEY]
#           S3_BUCKET_NAME        || the S3 bucket where the objects were uploaded
#           S3_INPUT_ZONE         || the S3 bucket zone where the objects were uploaded
#           S3_TARGET_ZONE        || the S3 bucket zone where the processed data wil be uploaded
#           S3_ZONE_ENDPOINTS_DIR || The directories in bucket zone where the object were uploaded, ex.: ENDPOINT1, ENDPOINT2
#           OBJECTS_KEY           || The OBJECTS_KEY_prefix are a list of objects, ex: Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}
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

def getS3Path(prefix: str,
              endpoint: str,
              subdir:str = "",
              typeFile: str = "",
              filename:str = ""):
    
    endpoint = endpoint = '_'.join(map(lambda sub: sub.capitalize(),
                                       endpoint.lower().split('_'))) if '_' in endpoint else endpoint.lower().capitalize()

    filename = f'{subdir}/{filename}'

    return f"{prefix}/{endpoint}/{filename}"

def extractData(prefix: str,
                endpoint: str,
                subdir: str = "",
                filename: str = "",
                typeFile: str = "",
                deepRead: bool = False):
    objects_key = getS3Path(prefix=prefix,
                            endpoint=endpoint,
                            subdir=subdir,
                            filename=filename,
                            typeFile=typeFile)
    # the files are uploaded in the following path: Zone/Entity/Year/Month/Day/Timestamp
    # if deepRead on it will read all subdir within Entity
    return spark.read.parquet(objects_key if not deepRead else f"{objects_key}/*/*/*/*/")

def transformData(entity: str,
                  df: DataFrame) -> DataFrame:
    if entity.lower() == "currency":
        df = df.select(col('id').alias("currency_id"),
                  col('currencySymbol').alias("currency_special_symbol"),
                  col('symbol').alias("currency_symbol"),
                  col("type").alias("currency_type"))
        
        df = df.withColumn("currency_type", substring(col("currency_type"), 1, 1))
                
        df.show()
        return df
    if entity.lower() == "crypto_data":
        df = df.select(col('id').alias("currency_id"),
                       col('changePercent24Hr').alias("diff_percent_24hr"),
                       col('maxSupply').alias("max_supply"),
                       col('supply'),
                       col('vwap24Hr').alias("vwap_24hr"),
                       col('volumeUsd24Hr').alias("vol_usd_24hr"),
                       col("marketCapUsd").alias("market_cap_usd"),
                       col('timestamp'))
        
        return df
    if entity.lower() == "currency_value":
        df.show()
        df = df.select(col('rateUsd').alias("rate_usd"),
                       col('timestamp'))
        
        return df
    
    raise Exception("Invalid endpoint")

# Since method Currency will almost always be the same
# This method avoid load duplicate data into Refined zone
def checkAndUpdateRowsWithinRefinedZone(load_prefix: str,
                                        entity: str,
                                        df: DataFrame):
  try:
    # extract data already saved
    # deepRead will allow the spark to read all the subdir within the /Zone/Entity/*
    df_saved = extractData(prefix=load_prefix,
                           endpoint=entity, deepRead=True)
    print("df_saved table: ")
    df_saved.show()
    if df.schema != df_saved.schema:
      df_saved.printSchema()
      df.printSchema()
      print("The data frames don't have the same schema")
      return
    else:
        diff_df = df.exceptAll(df_saved)
        if diff_df.count() == 0:
          print("The data frames has the same values.")
          
          return None
        else:
          print("The data frames has different values.")
          diff_df.show()
          return df.union(df_saved)
          
  except Exception as err:
    print(err)
    return df
    
    
# ETL functions
def loadData(prefix: str,
             entity: str,
             subdir_date: str,
             filename: str,
             df: DataFrame) -> DataFrame:
    
    path = getS3Path(prefix=prefix,
                     endpoint=entity)
    
    if entity.lower() == "currency":
        df = checkAndUpdateRowsWithinRefinedZone(load_prefix=prefix,
                                                 entity=entity,
                                                 df=df)
        if not df:
            print(f"{entity} wasn't uploaded into Refined zone 'cause there is no new data to update")
            return None
        
    df.write.parquet(f'{path}/{subdir_date}/{filename}',
                     mode="overwrite")

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

def execute_job():
    extract_prefix = f"s3://{S3_BUCKET_NAME}/{S3_INPUT_ZONE}"
    
    load_prefix = f"s3://{S3_BUCKET_NAME}/{S3_TARGET_ZONE}"

    print(f"[GLUE_JOB_SYSTEM] - Starting to processing data from {extract_prefix} to store into {load_prefix}...")
    
    OBJECTS_KEY = str(args['OBJECTS_KEY'])
    objects_key = OBJECTS_KEY.split(",")
    for endpoint in ENDPOINTS:
        
        _objects_key = filter(lambda object_key: endpoint.lower().capitalize() in object_key,
                              objects_key)
        
        print(f"[GLUE_JOB_SYSTEM] - Starting refining data stores in {endpoint}...")
        
        for object_key in _objects_key:
            filename = f'{getTimestampFromKeyObject(object_key=object_key)}'
            subdir= getDateSubDirFromKeyObject(object_key=object_key)
            
            print(f"[GLUE_JOB_SYSTEM] - The following pathfile within /{S3_TARGET_ZONE} will be processed: {subdir}/{filename}")
            
            print(f"[GLUE_JOB_SYSTEM] -  Starting extracting the data from {endpoint}...")
            
            df = extractData(prefix=extract_prefix,
                             subdir=subdir,
                             endpoint=endpoint,
                             filename=filename,)
            entities = []
            if endpoint.lower() == "rates":
                entities.append("Currency")
                entities.append("Currency_Value")
            else:
                entities.append("Crypto_Data")
            
            print("[GLUE_JOB_SYSTEM] - The data will be treat as source data for the following entities: {}".format(", ".join(entities)))
            
            for entity in entities:
                
                print(f"[GLUE_JOB_SYSTEM] - The data is being transformed into a {entity}'s data structured...")
                
                df_transformed = transformData(entity=entity,
                               df=df)

                print(f"[GLUE_JOB_SYSTEM] - The data transformed has the following scheme:")
                df_transformed.printSchema()
                
                print(f"[GLUE_JOB_SYSTEM] - Starting to load the transformed data into {load_prefix}...")
                
                loadData(prefix=load_prefix,
                         entity=entity,
                         filename= filename,
                         subdir_date=subdir,
                         df=df_transformed)
                
                print(f"[GLUE_JOB_SYSTEM] - The data was succefully loaded into {load_prefix}")

execute_job()
job.commit()