import sys
import json
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_list, array_join

tedx_dataset_path = "C:/Users/ste_g/Dropbox/Tecnologie Cloud e Mobile/Laboratorio virtuale/tedx_dataset-master/tedx_dataset.csv"

spark = SparkSession.builder.master("local").getOrCreate()
#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(tedx_dataset_path)
    
tedx_dataset.printSchema()

#### FILTER ITEMS WITH NULL POSTING KEY
count_items = tedx_dataset.count()
count_items_null = tedx_dataset.filter("idx is not null").count()

print(f"Number of items from RAW DATA {count_items}")
print(f"Number of items from RAW DATA with NOT NULL KEY {count_items_null}")


## READ TAGS DATASET
tags_dataset_path = "C:/Users/ste_g/Dropbox/Tecnologie Cloud e Mobile/Laboratorio virtuale/tedx_dataset-master/tags_dataset.csv"
tags_dataset = spark.read.option("header","true").csv(tags_dataset_path)



# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("idx").alias("idx_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset.join(tags_dataset_agg, tedx_dataset.idx == tags_dataset_agg.idx_ref, "left") \
    .drop("idx_ref") \
    .select(col("idx").alias("_id"), col("*")) \
    .drop("idx") \

tedx_dataset_agg.printSchema()
