# Databricks notebook source
# MAGIC %md
# MAGIC ## Importing libraries and modules

# COMMAND ----------

import requests
import json
import uuid
import time

from datetime import datetime, timezone
from pyspark.sql import Row

# COMMAND ----------

# MAGIC %md
# MAGIC ## Set constant variables

# COMMAND ----------

SELECTED_AIRPORTS = "dev_project.flight_delay_lakehouse.control_selected_airports"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
BRONZE_TABLE = "dev_project.flight_delay_lakehouse.bronze_weather_forecast_raw"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch waether API response
# MAGIC ## 

# COMMAND ----------

def fetch_weather(params: dict):
    for attempt in range(3):
        try:
            response = requests.get(WEATHER_URL, params=params, timeout=60)

            if response.status_code in (429, 403):
                print(f"Attempt {attempt + 1}: status {response.status_code} for params: {params}")
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return response.json(), response.status_code

        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1}: timeout for params: {params}")
            if attempt == 2:
                raise Exception(f"Weather API timed out after 3 attempts for params: {params}")
            time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: request error for params: {params}. Error: {e}")
            if attempt == 2:
                raise Exception(f"Weather API request failed after 3 attempts for params: {params}. Error: {e}")
            time.sleep(2 ** attempt)

    raise Exception(f"Weather API failed after retries for params: {params}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze row creation

# COMMAND ----------

def to_bronze_rows(payload: dict, params: dict, airport_code: str, lat: float, lon: float):
    rows = []
    ingested_at = datetime.now(timezone.utc).isoformat()
    run_id = str(uuid.uuid4())
    rows.append(
        Row(
            run_id=run_id,
            ingested_at=ingested_at,
            source="open-meteo",
            airport_code=airport_code,
            latitude=lat,
            longitude=lon,
            weather_kind="forecast",
            query_params=json.dumps(params),
            raw_response_json=json.dumps(payload)
        )
    )

    return rows

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to delta

# COMMAND ----------

def write_to_delta(rows: list):
    if not rows:
        print("No rows to write for this request.")
        return

    weather_forecast_df = spark.createDataFrame(rows)
    (
        weather_forecast_df.write
        .format("delta")
        .mode("append")
        .saveAsTable(BRONZE_TABLE)
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main pipeline

# COMMAND ----------

def main():
    airports_df = spark.table(SELECTED_AIRPORTS)
    airport_rows = airports_df.collect()

    for a in airport_rows:
        airport_code = a["airport_code"]
        lat = float(a["latitude"])   
        lon = float(a["longitude"])

        params = {
            "latitude":lat,
            "longitude":lon,
            "hourly": "temperature_2m,precipitation,wind_speed_10m",
            "forecast_days": 1,
            "timezone": "UTC"
        }

        print(f"Fetching forecast weather for {airport_code} ({lat}, {lon})")

        payload, status_code = fetch_weather(params)
        print(f"Status code for {airport_code}: {status_code}")

        rows = to_bronze_rows(payload, params, airport_code, lat, lon)
        write_to_delta(rows)

        time.sleep(2)
        

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run pipeline

# COMMAND ----------

main()