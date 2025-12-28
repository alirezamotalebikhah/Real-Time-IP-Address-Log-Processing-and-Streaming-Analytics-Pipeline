from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType


spark = SparkSession.builder \
    .appName("KafkaSparkStream") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


KAFKA_BROKER = "kafka:9092"  
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


query = df_json.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .option("numRows", 5) \
    .start()

query.awaitTermination()
