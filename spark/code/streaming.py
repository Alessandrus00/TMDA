import imp
from webbrowser import get
from pyspark.sql import SparkSession
import pyspark.sql.types as tp
from pyspark.sql.functions import from_json, col
from pyspark.ml import PipelineModel
from pyspark.ml.feature import IndexToString
from os import listdir
from time import sleep
from elasticsearch import Elasticsearch


# spark app name
APP_NAME = 'tmda_streaming'

# kafka broker and topics
KAFKA_BROKER = 'broker:29092'
KAFKA_TOPIC = 'sensors'

# model path
MODEL_PATH = '../tap/model'

# elastic host and index
ES_HOSTNAME = 'https://es01:9200'
ES_INDEX = 'sensors'


es = Elasticsearch(
    ES_HOSTNAME,
    ca_certs="../tap/certs/ca/ca.crt",
    basic_auth=("elastic", "progettotmda")
    )


# create dataframe schema
def get_schema():
    schema = tp.StructType([
        tp.StructField(name= 'user_id',       dataType= tp.IntegerType(),   nullable= True),
        tp.StructField(name= 'acc_mean',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'acc_min',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'acc_max',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'acc_stddev',    dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_mean',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_min',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_max',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_stddev',    dataType= tp.DoubleType(),    nullable= True)
        ])

    return schema


# spark initialization
def initialize_spark():
    spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    return spark


# read data from kafka
def read_from_kafka(spark):

    # get dataframe schema
    schema = get_schema()
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load() \
        .select(from_json(col("value").cast("string"), schema).alias("data")) \
        .selectExpr("data.*")
    
    return df


# when a batch of streaming data is ready 
# it will be sent to es through this function.
# This is called 'accrocco' (cit. Lemuel)
def process_batch(batch_df, batch_id):
    for idx, row in enumerate(batch_df.collect()):
        row_dict = row.asDict()
        id = f'{batch_id}-{idx}'
        resp = es.index(
            index=ES_INDEX, 
            id=id, 
            document=row_dict)
        print(resp)


# write to elasticsearch (in batch)
def write_to_es(df):
    df.writeStream \
        .foreach(process_batch) \
        .start() \
        .awaitTermination()


def main():

    # spark initialization
    spark = initialize_spark()

    # read data from kafka
    df = read_from_kafka(spark)

    # wait for the model to be created if it doesn't exist
    while len(listdir(MODEL_PATH)) == 0:
        sleep(5)
    
    # load the model
    model = PipelineModel.load(MODEL_PATH)

    # get a new df with predictions
    df = model.transform(df)

    # get back labels from indexed predictions
    ind_str = IndexToString(inputCol='prediction', outputCol='target', labels=['Bus', 'Car', 'Train', 'Still', 'Walking'])
    df = ind_str.transform(df)

    # remove features and other useless data
    df = df.select('user_id', 'target')

    # write data to elasticsearch
    write_to_es(df)



if __name__ == '__main__': main()