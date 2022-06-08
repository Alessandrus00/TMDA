import imp
from webbrowser import get
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
import pyspark.sql.types as tp
from pyspark.sql.functions import from_json, col, array
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
ES_HOSTNAME = 'http://elasticsearch:9200'
ES_INDEX = 'sensors'


# create dataframe schema
def get_schema():
    schema = tp.StructType([
        tp.StructField(name= 'timestamp',       dataType= tp.TimestampType(), nullable= True),
        tp.StructField(name= 'user_id',         dataType= tp.IntegerType(),   nullable= True),
        tp.StructField(name= 'acc_mean',        dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'acc_min',         dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'acc_max',         dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'acc_stddev',      dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_mean',       dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_min',        dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_max',        dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'gyro_stddev',     dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'latitude',        dataType= tp.DoubleType(),    nullable= True),
        tp.StructField(name= 'longitude',       dataType= tp.DoubleType(),    nullable= True)
        ])

    return schema


# spark initialization
def initialize_spark():
    sparkConf = SparkConf().set("es.nodes", "elasticsearch") \
                            .set("es.port", "9200")

    sc = SparkContext(appName=APP_NAME, conf=sparkConf)
    spark = SparkSession(sc)
    sc.setLogLevel("ERROR")

    return spark


def create_index():
    # define a mapping
    es_mapping = {
        "mappings": {
            "properties": 
                {
                    "timestamp":{"type":"date"},
                    "user_id": {"type": "integer"},
                    "target": {"type": "text", "fielddata": True},
                    "location": {"type": "geo_point"}
                }
        }
    }
    es = Elasticsearch(hosts=ES_HOSTNAME) 
    # make an API call to the Elasticsearch cluster
    # and have it return a response:
    response = es.indices.create(
        index=ES_INDEX,
        body=es_mapping,
        ignore=400 # ignore 400 already exists code
    )
    # check if the response was successful
    if 'acknowledged' in response:
        if response['acknowledged'] == True:
            print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])


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


# write to elasticsearch (in batch)
def write_to_es(df):
    df.writeStream \
        .option("checkpointLocation", "/save/location") \
        .format("es") \
        .start(ES_INDEX) \
        .awaitTermination()

def main():

    # spark initialization
    spark = initialize_spark()

    # create es index and mapping
    create_index()

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

    # create a 'location' array. Needed to send a valid geo point to es 
    df = df.withColumn('location', array(col('longitude'), col('latitude')))

    # remove features and other useless data
    df = df.select('timestamp', 'user_id', 'target', 'location')

    # Write the stream to elasticsearch
    write_to_es(df)



if __name__ == '__main__': main()