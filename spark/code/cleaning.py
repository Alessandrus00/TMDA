import math
from pyspark.sql import SparkSession
import pyspark.sql.types as tp
from pyspark.sql.functions import from_json, col, to_timestamp, session_window, udf, max, min, mean, stddev

# spark app name
APP_NAME = 'tmda_cleaning'

# kafka broker and topics
KAFKA_BROKER = 'broker:29092'
KAFKA_TOPIC_RAW = 'sensors-raw'
KAFKA_TOPIC_CLEAN = 'sensors'


# create and get the input dataframe schema
# note that logstash (ingestor) send to kafka a json of strings (we do casting later)
def get_schema():
    schema = tp.StructType([
        tp.StructField(name= 'timestamp',   dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'user_id',     dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'acc_x',       dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'acc_y',       dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'acc_z',       dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'gyro_x',      dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'gyro_y',      dataType= tp.StringType(),  nullable= True),
        tp.StructField(name= 'gyro_z',      dataType= tp.StringType(),  nullable= True),
        ])

    return schema


# convert 'user_id' string to integer
# and sensors data from string to double
def cast_data(df):
    # convert event timestamp to the type Timestamp of spark 
    df = df.withColumn("timestamp", col("timestamp").cast(tp.TimestampType()))
    df = df.withColumn("user_id", col("user_id").cast(tp.IntegerType()))
    df = df.withColumn("acc_x", col("acc_x").cast(tp.DoubleType()))
    df = df.withColumn("acc_y", col("acc_y").cast(tp.DoubleType()))
    df = df.withColumn("acc_z", col("acc_z").cast(tp.DoubleType()))
    df = df.withColumn("gyro_x", col("gyro_x").cast(tp.DoubleType()))
    df = df.withColumn("gyro_y", col("gyro_y").cast(tp.DoubleType()))
    df = df.withColumn("gyro_z", col("gyro_z").cast(tp.DoubleType()))

    return df


# compute magnitude of sensors data
@udf(returnType=tp.DoubleType())
def compute_magnitude(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)


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
        .option("subscribe", KAFKA_TOPIC_RAW) \
        .option("startingOffsets", "earliest") \
        .load() \
        .select(from_json(col("value").cast("string"), schema).alias("data")) \
        .selectExpr("data.*")
    
    return df


# aggragate data in order to extract features (like in the training phase).
# By default data will be sent to kafka in batches of 5 sec for each user
# so we always aggregate 5 sec of data
def extract_features(df):
    df = df \
        .withColumn('acc', compute_magnitude(col('acc_x'), col('acc_y'), col('acc_z'))) \
        .withColumn('gyro', compute_magnitude(col('gyro_x'), col('gyro_y'), col('gyro_z'))) \
        .withWatermark('timestamp', '2 seconds') \
        .groupBy(
            # after 2 sec of lacking data from a user we end the session
            session_window('timestamp', '2 seconds'),
            'user_id') \
        .agg(mean('acc').alias('acc_mean'),
            min('acc').alias('acc_min'),
            max('acc').alias('acc_max'),
            stddev('acc').alias('acc_stddev'),
            mean('gyro').alias('gyro_mean'),
            min('gyro').alias('gyro_min'),
            max('gyro').alias('gyro_max'),
            stddev('gyro').alias('gyro_stddev')) \
        .na.fill(value=0)
    
    return df

# write data to kafka
def write_to_kafka(df):
    df.selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format('kafka') \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("topic", KAFKA_TOPIC_CLEAN) \
        .option("checkpointLocation", "/save/location") \
        .outputMode('append') \
        .start() \
        .awaitTermination()


def main():

    # spark initialization
    spark = initialize_spark()

    # read data from kafka
    df = read_from_kafka(spark)

    # cast string data to its numeric counterpart
    df = cast_data(df)

    # check if we are streaming data from kafka correctly
    print("Streaming DataFrame : ", df.isStreaming)

    # extract features from data
    df = extract_features(df)
    
    # print the final dataframe schema
    df.printSchema()

    # write aggragated data to a new kafka topic
    write_to_kafka(df)



if __name__ == '__main__': main()