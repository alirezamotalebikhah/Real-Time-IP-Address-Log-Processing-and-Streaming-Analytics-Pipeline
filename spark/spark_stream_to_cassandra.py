from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType


spark = SparkSession.builder \
    .appName("KafkaToCassandraStream") \
    .master("local[*]") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,"
            "com.datastax.spark:spark-cassandra-connector_2.13:3.5.0") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


KAFKA_BROKER = "172.28.0.3:9092"
TOPIC = "logs"


df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()


df_parsed = df.selectExpr("CAST(value AS STRING) as json_value")

schema = StructType() \
    .add("log_timestamp", DoubleType()) \
    .add("ip", StringType()) \
    .add("url", StringType())

df_json = df_parsed.select(from_json(col("json_value"), schema).alias("data")).select("data.*")


def write_to_cassandra(batch_df, epoch_id):
    batch_df.write \
        .format("org.apache.spark.sql.cassandra") \
        .option("keyspace", "logs_ks") \
        .option("table", "logs") \
        .mode("append") \
        .save()


query = df_json.writeStream \
    .foreachBatch(write_to_cassandra) \
    .outputMode("update") \
    .start()

query.awaitTermination()
