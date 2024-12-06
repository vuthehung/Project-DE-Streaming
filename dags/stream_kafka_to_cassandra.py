from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 12, 1),
}

with DAG('stream_kafka_to_cassandra',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    start_streaming = BashOperator(
        task_id='run_spark_streaming',
        bash_command= "spark-submit --master spark://localhost:7077 ../spark_stream.py"
    )
