from genericpath import exists
import shutil
from time import sleep
import pandas as pd
import glob
import os
import zipfile
from time import sleep
from random import randint
from datetime import datetime, timedelta


# define a list of attributes to send to the pipeline
SENSORS_DATASET_COLS = [
    'timestamp',
    'user_id',
    'acc_x',
    'acc_y',
    'acc_z',
    'gyro_x',
    'gyro_y',
    'gyro_z',
    'latitude',
    'longitude'
    ]


# get the earliest generated zipfile
def get_earliest_zipfile(zip_list):
    #earliest_zip = min(zip_list, key=os.path.getctime)
    earliest_zip = min(zip_list, key=os.path.basename)
    return earliest_zip


# unzip a zipfile
def unzip(file):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall()


# filter rows over the 5 sec window
def get_5sec(df):
    return df[df['Time (s)']< 5]


# convert the timestamp to a datetime format
def convert_timestamp(df_time):
    start_time = df_time.iloc[0]['system time text'][:23]
    start_time_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')

    return start_time_dt
    
# update sensors.csv with new extracted values
def update_sensors_csv(file):
    unzip(file)

    # read csv extracted from the zip file
    df_acc = pd.read_csv('Accelerometer.csv')
    df_gyro = pd.read_csv('Gyroscope.csv')
    df_location = pd.read_csv('Location.csv')
    df_time = pd.read_csv('meta/time.csv')

    df_acc = get_5sec(df_acc)
    df_gyro = get_5sec(df_gyro)

    # create sensors.csv if not exists
    if not exists('../sensors.csv'):
        pd.DataFrame(columns= SENSORS_DATASET_COLS).to_csv('../sensors.csv', index=False)
         
    df_sensors = pd.read_csv('../sensors.csv')
    start_time = convert_timestamp(df_time) 
    min_len = min(len(df_acc), len(df_gyro))

    # generate a random user ID (becouse we don't have one)
    user_id = randint(1,10)
    # add raw data to sensors.csv
    for i in range(min_len):
        new_df = pd.DataFrame([[
            start_time + timedelta(seconds=float(df_acc.iloc[i,0])),
            user_id,
            df_acc.iloc[i,1],
            df_acc.iloc[i,2],
            df_acc.iloc[i,3],
            df_gyro.iloc[i,1],
            df_gyro.iloc[i,2],
            df_gyro.iloc[i,3],
            df_location.iloc[0,1],
            df_location.iloc[0,2]]],
            columns=SENSORS_DATASET_COLS)

        df_sensors = pd.concat([df_sensors, new_df])
    
    # save the updated dataframe 
    df_sensors.to_csv('../sensors.csv', index=False)

    # remove zip file and extracted csv (we already have them in sensors.csv)
    os.remove('Accelerometer.csv')
    os.remove('Gyroscope.csv')
    os.remove('Location.csv')
    os.remove(file)
    shutil.rmtree('meta')


def main():

    # listen to new entry in 'zips' folder
    while(True):
        # get a list of zip files
        zip_list = glob.glob('*.zip') 
        # if is not empty update sensors.csv, else sleep
        if len(zip_list) > 0:
            zf = get_earliest_zipfile(zip_list)
            update_sensors_csv(zf)
        sleep(5)

        

if __name__ == '__main__': main()