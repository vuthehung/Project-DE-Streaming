from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from cassandra.cluster import Cluster

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 12, 1),
}

def create_keyspace_table():
    cluster = Cluster(['localhost'])
    session = cluster.connect()

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    print("Keyspace created successfully!")

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
    print("Table created successfully!")

with DAG('create_cassandra_keyspace_table',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    create_task = PythonOperator(
        task_id='create_keyspace_table',
        python_callable=create_keyspace_table
    )
