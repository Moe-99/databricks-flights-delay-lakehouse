# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

from pyspark.sql.functions import from_json, col, to_timestamp, trim, when, lower
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create flights bronze dataframe

# COMMAND ----------

bronze_flights_df = spark.table("dev_project.flight_delay_lakehouse.bronze_flights_raw")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create flights silver schema

# COMMAND ----------

flights_schema = StructType([
    StructField("flight_date", StringType(), True),
    StructField("flight_status", StringType(), True),

    StructField("departure", StructType([
        StructField("airport", StringType(), True),
        StructField("iata", StringType(), True),
        StructField("icao", StringType(), True),
        StructField("delay", IntegerType(), True),
        StructField("scheduled", StringType(), True),
        StructField("estimated", StringType(), True),
        StructField("actual", StringType(), True),
    ]), True),

   StructField("arrival", StructType([
        StructField("airport", StringType(), True),
        StructField("iata", StringType(), True),
        StructField("icao", StringType(), True),
        StructField("delay", IntegerType(), True),
        StructField("scheduled", StringType(), True),
        StructField("estimated", StringType(), True),
        StructField("actual", StringType(), True),
    ]), True),

  StructField("airline", StructType([
        StructField("name", StringType(), True),
        StructField("iata", StringType(), True),
        StructField("icao", StringType(), True),
    ]), True),

    StructField("flight", StructType([
        StructField("number", StringType(), True),
        StructField("iata", StringType(), True),
        StructField("icao", StringType(), True),
    ]), True),
])



# COMMAND ----------

# MAGIC %md
# MAGIC ## Parse bronze raw json record 

# COMMAND ----------

parsed_flights_df = bronze_flights_df.withColumn(
    "flights_parsed",
    from_json(col("raw_record_json"), flights_schema)
)


# COMMAND ----------

# MAGIC %md
# MAGIC ## Create flights silver dataframe

# COMMAND ----------

flights_silver_df = (
    parsed_flights_df
    .select(
        col("flights_parsed.flight_date").alias("flight_date"),

        when(trim(col("flights_parsed.flight.iata")) == "", None)
            .otherwise(trim(col("flights_parsed.flight.iata")))
            .alias("flight_iata"),

        when(trim(col("flights_parsed.flight.icao")) == "", None)
            .otherwise(trim(col("flights_parsed.flight.icao")))
            .alias("flight_icao"),

        when(trim(col("flights_parsed.flight.number")) == "", None)
            .otherwise(trim(col("flights_parsed.flight.number")))
            .alias("flight_number"),

        when(
            lower(trim(col("flights_parsed.airline.name"))) == "empty",
            None
        ).otherwise(trim(col("flights_parsed.airline.name")))
         .alias("airline_name"),

        when(trim(col("flights_parsed.airline.iata")) == "", None)
            .otherwise(trim(col("flights_parsed.airline.iata")))
            .alias("airline_iata"),

        when(trim(col("flights_parsed.airline.icao")) == "", None)
            .otherwise(trim(col("flights_parsed.airline.icao")))
            .alias("airline_icao"),

        col("flights_parsed.flight_status").alias("flight_status"),

        when(trim(col("flights_parsed.departure.iata")) == "", None)
            .otherwise(trim(col("flights_parsed.departure.iata")))
            .alias("dep_airport_iata"),

        trim(col("flights_parsed.departure.airport")).alias("dep_airport_name"),

        when(trim(col("flights_parsed.departure.icao")) == "", None)
            .otherwise(trim(col("flights_parsed.departure.icao")))
            .alias("dep_airport_icao"),

        when(trim(col("flights_parsed.arrival.iata")) == "", None)
            .otherwise(trim(col("flights_parsed.arrival.iata")))
            .alias("arr_airport_iata"),

        trim(col("flights_parsed.arrival.airport")).alias("arr_airport_name"),

        when(trim(col("flights_parsed.arrival.icao")) == "", None)
            .otherwise(trim(col("flights_parsed.arrival.icao")))
            .alias("arr_airport_icao"),

        to_timestamp(col("flights_parsed.departure.scheduled")).alias("dep_scheduled_ts"),
        to_timestamp(col("flights_parsed.departure.estimated")).alias("dep_estimated_ts"),
        to_timestamp(col("flights_parsed.departure.actual")).alias("dep_actual_ts"),

        to_timestamp(col("flights_parsed.arrival.scheduled")).alias("arr_scheduled_ts"),
        to_timestamp(col("flights_parsed.arrival.estimated")).alias("arr_estimated_ts"),
        to_timestamp(col("flights_parsed.arrival.actual")).alias("arr_actual_ts"),

        col("flights_parsed.departure.delay").cast("int").alias("dep_delay_minutes"),
        col("flights_parsed.arrival.delay").cast("int").alias("arr_delay_minutes"),

        col("run_id"),
        col("ingested_at")
    )
    .filter(
        col("dep_airport_iata").isNotNull() &
        col("arr_airport_iata").isNotNull()
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Writing to flights silver delta table

# COMMAND ----------

(
    flights_silver_df.write
    .mode("overwrite")
    .format("delta")
    .saveAsTable("dev_project.flight_delay_lakehouse.silver_flights")
)