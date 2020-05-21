###### TEDx-Load-Aggregate-Model
######

import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join, struct

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job


##### FROM FILES
tedx_dataset_path = ""  # path to tedx_dataset.csv

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()


glueContext = GlueContext(sc)
spark = glueContext.spark_session


    
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read.option("header","true").option("quote", "\"").option("escape", "\"").csv(tedx_dataset_path)
    
tedx_dataset.printSchema()


#### FILTER ITEMS WITH NULL POSTING KEY
count_items = tedx_dataset.count()
count_items_null = tedx_dataset.filter("idx is not null").count()
print(f"Number of items from RAW DATA {count_items}")
print(f"Number of items from RAW DATA with NOT NULL KEY {count_items_null}")



## READ TAGS DATASET
tags_dataset_path = ""  #path to tags_dataset.csv
tags_dataset = spark.read.option("header","true").csv(tags_dataset_path)


# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("idx").alias("idx_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset.join(tags_dataset_agg, tedx_dataset.idx == tags_dataset_agg.idx_ref, "left") \
    .drop("idx_ref") \
    .select(col("idx").alias("_id"), col("*")) \
    .drop("idx") \

tedx_dataset_agg.printSchema()

# ADD INFORMATION ABOUT NEXT_TALK 
next_dataset_path = ""      #path to watch_next_dataset.csv
next_dataset = spark.read.option("header","true").csv(next_dataset_path).distinct().drop('url')

print(f"Number of items from RAW DATA {next_dataset.count()}")

print("next_dataset schema")
next_dataset.printSchema()

next_dataset_agg = next_dataset.join(tedx_dataset_agg, tedx_dataset_agg._id == next_dataset.watch_next_idx) \
    .drop("watch_next_idx").groupBy('idx').agg(collect_list(struct(col('_id').alias('next_id'),'main_speaker','title','url')).alias("next_talks")) \
        .select('idx','next_talks') 

print("next_dataset_agg schema")
next_dataset_agg.printSchema()


final_dataset = tedx_dataset_agg.join(next_dataset_agg, tedx_dataset_agg._id == next_dataset_agg.idx, 'left') \
    .drop("idx").select("*")

print("final_dataset schema")
final_dataset.printSchema()



mongo_uri = "mongodb://tcmcluster-shard-00-00-kxu1l.mongodb.net:27017,tcmcluster-shard-00-01-kxu1l.mongodb.net:27017,tcmcluster-shard-00-02-kxu1l.mongodb.net:27017"

write_mongo_options = {
    "uri": mongo_uri,
    "database": "unibg_tedx",
    "collection": "mytedx_data",
    "username": "",
    "password": "",
    "ssl": "true",
    "ssl.domain_match": "false"}


from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(final_dataset, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)