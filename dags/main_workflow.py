from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 12, 1),
}

with DAG('main_workflow',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    trigger_stream_api_dag = TriggerDagRunOperator(
        task_id='trigger_stream_data_from_api',
        trigger_dag_id='stream_data_from_api',
    )

    trigger_create_cassandra_dag = TriggerDagRunOperator(
        task_id='trigger_create_cassandra_keyspace_table',
        trigger_dag_id='create_cassandra_keyspace_table',
    )

    trigger_test_spark_dag = TriggerDagRunOperator(
        task_id='trigger_test_spark_kafka',
        trigger_dag_id='test_spark_kafka_connection',
    )

    trigger_stream_kafka_dag = TriggerDagRunOperator(
        task_id='trigger_stream_kafka_to_cassandra',
        trigger_dag_id='stream_kafka_to_cassandra',
    )

    (trigger_stream_api_dag >> trigger_create_cassandra_dag >>
     trigger_test_spark_dag >> trigger_stream_kafka_dag)
