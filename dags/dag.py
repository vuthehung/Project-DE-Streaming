import uuid
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator, BashOperator
import subprocess

default_args = {
    'owner': 'airscholar',
    'start_date': datetime(2024, 7, 23, 10, 00),
    'retries': 3,
    'retry_delay': 300
}

def create_cassandra_schema():
    from cassandra.cluster import Cluster
    cluster = Cluster(['localhost'])
    session = cluster.connect()
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS spark_streams.created_users (
            id UUID PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            address TEXT,
            post_code TEXT,
            email TEXT,
            username TEXT,
            registered_date TEXT,
            phone TEXT,
            picture TEXT);
    """)
    print("Cassandra Keyspace and Table created successfully!")

def stream_data():
    import json
    from kafka import KafkaProducer
    import time
    import requests

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    curr_time = time.time()

    while time.time() < curr_time + 60:  # Stream for 1 minute
        res = requests.get("https://randomuser.me/api/").json()['results'][0]
        data = {
            'id': str(uuid.uuid4()),
            'first_name': res['name']['first'],
            'last_name': res['name']['last'],
            'gender': res['gender'],
            'address': f"{res['location']['street']['number']} {res['location']['street']['name']}, "
                       f"{res['location']['city']}, {res['location']['state']}, {res['location']['country']}",
            'post_code': res['location']['postcode'],
            'email': res['email'],
            'username': res['login']['username'],
            'registered_date': res['registered']['date'],
            'phone': res['phone'],
            'picture': res['picture']['medium']
        }
        producer.send('users_created', json.dumps(data).encode('utf-8'))
    print("Streaming complete!")

with DAG('user_automation',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    create_schema_task = PythonOperator(
        task_id='create_cassandra_schema',
        python_callable=create_cassandra_schema
    )

    stream_data_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )

    process_stream_task = BashOperator(
        task_id='process_stream_task',
        bash_command="""
            spark-submit /opt/airflow/code/spark_stream.py
        """
    )

    stream_data_task >> create_schema_task >> process_stream_task