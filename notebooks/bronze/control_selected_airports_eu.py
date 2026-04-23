# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

from pyspark.sql.functions import col

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create selected airports df

# COMMAND ----------

selected_airports = (
    spark.table("dev_project.flight_delay_lakehouse.candidate_airports_eu")
    .filter(
        col("airport_code").isin(
        "AMS", "LHR", "LGW", "CDG", "FRA", "MUC", "MAD", "BCN", "FCO", "ZRH",
        "VIE", "CPH", "ARN", "OSL", "HEL", "DUB", "MAN", "BHX", "EDI", "LIS",
        "OPO", "BRU", "ATH", "WAW", "PRG", "BUD", "OTP", "SOF", "RIX", "TLL",
        "VNO", "KEF", "HAM", "DUS", "CGN", "STR", "HAJ", "NUE", "LEJ", "BRS",
        "LPL", "LTN", "BLL", "GVA", "NCE", "TLS", "MXP", "LIN", "NAP", "PMI"
    ))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write selected airports to delta

# COMMAND ----------

(
    selected_airports.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("dev_project.flight_delay_lakehouse.control_selected_airports")
)

                     