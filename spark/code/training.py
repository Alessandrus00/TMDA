from random import seed
import pandas as pd
from os.path import exists
from os import listdir
import pyspark.sql.types as tp
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier, LinearSVC, NaiveBayes, LogisticRegression, OneVsRest, GBTClassifier
from pyspark.ml.feature import StringIndexer
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.sql.types import FloatType
import pyspark.sql.functions as F


# spark app name
APP_NAME = 'tmda_training'

# datasets paths
DATASET_PATH = '../tap/spark/dataset/dataset_5secondWindow.csv'
CLEAN_DATASET_PATH = '../tap/spark/dataset/sensors_training_clean.csv'

# model path
MODEL_PATH = '../tap/model'

# features
FEATURES = [
    'acc_mean',
    'acc_min',
    'acc_max',
    'acc_stddev',
    'gyro_mean',
    'gyro_min',
    'gyro_max',
    'gyro_stddev'
    ]


# create and return training set schema
def get_schema():

    schema = tp.StructType([
        tp.StructField(name= 'acc_mean',     dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'acc_min',     dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'acc_max',     dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'acc_stddev',  dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'gyro_mean',     dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'gyro_min',     dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'gyro_max',     dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'gyro_stddev',  dataType= tp.DoubleType(),  nullable= True),
        tp.StructField(name= 'target',      dataType= tp.StringType(),  nullable= True)
        ])

    return schema



def create_clean_dataset():

    # if the refined dataset already exists return immediately
    if exists(CLEAN_DATASET_PATH):
        return

    # read the raw dataset
    df = pd.read_csv(DATASET_PATH)

    df.rename(columns={
        'android.sensor.accelerometer#mean': 'acc_mean',
        'android.sensor.accelerometer#min' : 'acc_min',
        'android.sensor.accelerometer#max' : 'acc_max',
        'android.sensor.accelerometer#std' : 'acc_stddev',
        'android.sensor.gyroscope#mean' : 'gyro_mean',
        'android.sensor.gyroscope#min' : 'gyro_min',
        'android.sensor.gyroscope#max' : 'gyro_max',
        'android.sensor.gyroscope#std' : 'gyro_stddev'  
        },
        inplace=True)

    df = df[FEATURES + ['target']]

    df.fillna(value=0, inplace=True)

    # store the new dataset
    df.to_csv(CLEAN_DATASET_PATH, index=False)


def initialize_spark():

    # spark session initializzation
    spark = SparkSession.builder.appName(APP_NAME) \
        .config('spark.files.overwrite', 'true') \
        .getOrCreate()

    spark.sparkContext.setLogLevel('ERROR')

    return spark


def read_dataset(spark):

    # get the schema
    schema = get_schema()

    # load dataset
    df = spark.read.csv(CLEAN_DATASET_PATH,
                    schema = schema,
                    header = True)
    return df


# create a pipeline to preprocess data and run
# a tuned Random Forest classifier to extract value from them
def create_pipeline(df):

    # used to have numeric labels, instead of strings
    str_indx = StringIndexer(inputCol = 'target', outputCol = 'target_index', stringOrderType="alphabetAsc", handleInvalid = 'keep')

    # spark needs features as a single vector
    asb = VectorAssembler(inputCols=FEATURES, outputCol='features')

    # create random forest classifier
    #rf = RandomForestClassifier(featuresCol= 'features', labelCol= 'target_index', numTrees=100)

    gbt = GBTClassifier(featuresCol= 'features', labelCol= 'target_index', maxDepth=10, seed=1000)

    ovr = OneVsRest(featuresCol= 'features', labelCol= 'target_index', classifier=gbt)

    # create the pipeline
    pipeline = Pipeline(stages= [str_indx, asb, ovr])

    return pipeline


# training and evaluation of the model
def train_and_evaluate(df, pipeline):

    # split dataset
    (training_data, test_data) = df.randomSplit([ .8, .2 ], seed= 1001)

    # fit the model with training data and make predictions
    pipeline_model = pipeline.fit(training_data)
    predictions = pipeline_model.transform(test_data)

    # create an evaluator to compute accuracy on predictions
    evaluator = MulticlassClassificationEvaluator(
        labelCol='target_index', 
        predictionCol='prediction', 
        metricName='accuracy'
    )

    # accuracy
    accuracy = evaluator.evaluate(predictions)
    print('Test accuracy = ', accuracy)

    # confusion matrix
    preds_and_labels = predictions.select(['prediction','target_index']).withColumn('target_index', F.col('target_index').cast(FloatType())).orderBy('prediction')
    preds_and_labels = preds_and_labels.select(['prediction','target_index'])
    metrics = MulticlassMetrics(preds_and_labels.rdd.map(tuple))
    print(metrics.confusionMatrix().toArray())

    return pipeline_model


def main():

    # if a model already exists return immediately.
    # if you want to retrain the model, please delete the existing model folder
    if len(listdir(MODEL_PATH)) > 0:
        return

    # clean data
    create_clean_dataset()

    # spark initialization
    spark = initialize_spark()

    # read the clean dataset from spark
    df = read_dataset(spark)

    # create a pipeline and a cross validator for tuning
    pipeline = create_pipeline(df)

    # train a model and evaluate its accuracy and confusion matrix
    pipeline_model = train_and_evaluate(df, pipeline)

    # save the model to disk for later use
    pipeline_model.write().overwrite().save(MODEL_PATH)



if __name__ == '__main__': main()