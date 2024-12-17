import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType


def create_spark_connection():
    try:
        spark_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,"
                                           "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") \
            .config('spark.cassandra.connection.host', 'localhost') \
            .getOrCreate()

        spark_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
        return spark_conn
    except Exception as e:
        logging.error(f"Couldn't create Spark session due to exception: {e}")
        return None


def connect_to_kafka(spark_conn):
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'localhost:9092') \
            .option('subscribe', 'users_created') \
            .option('startingOffsets', 'earliest') \
            .load()
        logging.info("Kafka DataFrame created successfully")
        return spark_df
    except Exception as e:
        logging.error(f"Kafka DataFrame could not be created: {e}")
        return None


def create_selection_df_from_kafka(spark_df):
    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("post_code", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False)
    ])

    return spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col('value'), schema).alias('data')).select("data.*")


if __name__ == "__main__":
    spark_conn = create_spark_connection()

    if spark_conn:
        spark_df = connect_to_kafka(spark_conn)
        if spark_df:
            selection_df = create_selection_df_from_kafka(spark_df)
            logging.info("Starting streaming query...")

            query = (selection_df.writeStream
                     .format("org.apache.spark.sql.cassandra")
                     .option('checkpointLocation', '/tmp/checkpoint')
                     .option('keyspace', 'spark_streams')
                     .option('table', 'created_users')
                     .start())

            query.awaitTermination()