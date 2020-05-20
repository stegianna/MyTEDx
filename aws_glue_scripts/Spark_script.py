import sys
import json
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_list, array_join, struct

tedx_dataset_path = "tedx_dataset.csv"

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
tags_dataset_path = "tags_dataset.csv"
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
next_dataset_path = "watch_next_dataset.csv"
next_dataset = spark.read.option("header","true").csv(next_dataset_path).distinct().drop('url')

print(f"Number of items from RAW DATA {next_dataset.count()}")

print("Next_dataset schema")
next_dataset.printSchema()

next_dataset_agg = next_dataset.join(tedx_dataset_agg, tedx_dataset_agg._id == next_dataset.watch_next_idx) \
    .drop("watch_next_idx").groupBy('idx').agg(collect_list(struct(col('_id').alias('next_id'),'main_speaker','title','url')).alias("next_talks")) \
        .select('idx','next_talks') 

print("next_dataset_agg schema")
next_dataset_agg.printSchema()


final_dataset = tedx_dataset_agg.join(next_dataset_agg, tedx_dataset_agg._id == next_dataset_agg.idx, 'left') \
    .drop("idx").select("*")

print("final dataset schema")
final_dataset.printSchema()

print(final_dataset.toJSON().first())

