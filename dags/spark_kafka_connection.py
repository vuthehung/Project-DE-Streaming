from airflow import DAG
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 12, 1),
}

def test_spark_kafka_connection():
    try:
        spark = SparkSession.builder \
            .appName('TestSparkKafka') \
            .config('spark.jars.packages', "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") \
            .getOrCreate()

        spark.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'localhost:9092') \
            .option('subscribe', 'users_created') \
            .load()
        print("Spark and Kafka connection established successfully!")
        spark.stop()
    except Exception as e:
        print(f"Connection failed: {e}")

with DAG('test_spark_kafka_connection',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    test_task = PythonOperator(
        task_id='test_spark_kafka',
        python_callable=test_spark_kafka_connection
    )
