# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

from pyspark.sql.functions import col, from_json, arrays_zip, explode, to_timestamp, trim
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating bronze weather dataframe

# COMMAND ----------

bronze_weather_df = spark.table("dev_project.flight_delay_lakehouse.bronze_weather_raw")
weather_schema = StructType([
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("timezone", StringType(), True),
    StructField("hourly", StructType([
        StructField("time", ArrayType(StringType()), True),
        StructField("temperature_2m", ArrayType(DoubleType()), True),
        StructField("precipitation", ArrayType(DoubleType()), True),
        StructField("wind_speed_10m", ArrayType(DoubleType()), True)
    ]), True)
])


# COMMAND ----------

# MAGIC %md
# MAGIC ## Parse the raw JSON string into a structured column

# COMMAND ----------

parsed_weather_df = bronze_weather_df.withColumn("weather_parsed", from_json(col("raw_response_json"), weather_schema))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Zip the hourly arrays together so index positions stay aligned

# COMMAND ----------

zipped_weather_df = parsed_weather_df.withColumn("hourly_zipped", arrays_zip(
    col("weather_parsed.hourly.time"),
    col("weather_parsed.hourly.temperature_2m"),
    col("weather_parsed.hourly.precipitation"),
    col("weather_parsed.hourly.wind_speed_10m")
))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Explode into one row per hour

# COMMAND ----------

exploded_weather_df = zipped_weather_df.withColumn("hourly_row", explode(col("hourly_zipped")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Select final Silver columns with clean names

# COMMAND ----------

silver_weather_df = (
    exploded_weather_df
    .select(
        trim(col("airport_code")).alias("airport_code"),
        col("latitude"),
        col("longitude"),
        to_timestamp(col("hourly_row.time")).alias("weather_ts"),
        col("hourly_row.temperature_2m").alias("air_temperature_2m_c"),
        col("hourly_row.precipitation").alias("precipitation_mm"),
        col("hourly_row.wind_speed_10m").alias("wind_speed_10m_kmh"),
        trim(col("weather_kind")).alias("weather_kind"),
        col("ingested_at")
    )
    .filter(col("weather_ts").isNotNull())
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Silver table

# COMMAND ----------

(silver_weather_df.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dev_project.flight_delay_lakehouse.silver_weather_hourly"))

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC