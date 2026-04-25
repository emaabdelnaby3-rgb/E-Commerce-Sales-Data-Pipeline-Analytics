"""Spark Structured Streaming job for cleaning, dedupe, and aggregation."""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, window
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

schema = StructType(
    [
        StructField("event_type", StringType(), False),
        StructField("occurred_at", StringType(), False),
        StructField("case_id", IntegerType(), True),
        StructField("organization_id", IntegerType(), True),
        StructField("amount_requested", IntegerType(), True),
    ]
)


def main():
    spark = SparkSession.builder.appName("charity-events-stream").getOrCreate()

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "charity_events")
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = raw.select(from_json(col("value").cast("string"), schema).alias("e")).select("e.*")

    cleaned = (
        parsed.withColumn("occurred_ts", to_timestamp("occurred_at"))
        .dropna(subset=["event_type", "occurred_ts"])
        .dropDuplicates(["event_type", "case_id", "occurred_at"])
    )

    aggregates = (
        cleaned.filter(col("event_type") == "case_created")
        .groupBy(window(col("occurred_ts"), "1 day"), col("organization_id"))
        .count()
    )

    query = (
        aggregates.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .start()
    )
    query.awaitTermination()


if __name__ == "__main__":
    main()
