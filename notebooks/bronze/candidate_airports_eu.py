# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

from pyspark.sql.functions import col

# COMMAND ----------

# MAGIC %md
# MAGIC ## Creating EU candidate airports

# COMMAND ----------

candidate_airports = (
    spark.table("dev_project.flight_delay_lakehouse.bronze_airports_raw")
    .filter(
        (col("continent") == "EU") &
        (col("iata_code").isNotNull()) &
        (col("type").isin("medium_airport", "large_airport"))
)
.select(
    col("iata_code").alias("airport_code"),
    col("name").alias("airport_name"),
    col("iso_country").alias("country"),
    col("latitude_deg").alias("latitude"),
    col("longitude_deg").alias("longitude"),
    col("type")
)
.dropDuplicates(["airport_code"])
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Writing candidate airports to delta

# COMMAND ----------

(candidate_airports.write
 .mode("overwrite")
 .format("delta")
 .saveAsTable("dev_project.flight_delay_lakehouse.candidate_airports_eu")
)

 