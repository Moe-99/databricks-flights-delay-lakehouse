# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

import requests
import json
import uuid
import time

from datetime import datetime, timezone, timedelta
from pyspark.sql import Row

# COMMAND ----------

# MAGIC %md
# MAGIC ## Set constant variables

# COMMAND ----------

SELECTED_AIRPORTS = "dev_project.flight_delay_lakehouse.control_selected_airports"
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
BRONZE_TABLE = "dev_project.flight_delay_lakehouse.bronze_weather_forecast_raw"

dbutils.widgets.text("start_date", "")
dbutils.widgets.text("end_date", "")

start_date = dbutils.widgets.get("start_date").strip()
end_date = dbutils.widgets.get("end_date").strip()

if not end_date:
    end_date = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d")

if not start_date:
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    start_date = (end_dt - timedelta(days=31)).strftime("%Y-%m-%d")

print(f"Archive backfill window: {start_date} to {end_date}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch waether API response

# COMMAND ----------

def fetch_weather(params: dict):
    last_error = None

    for attempt in range(3):
        try:
            response = requests.get(WEATHER_URL, params=params, timeout=60)

            print(f"Attempt {attempt + 1} status: {response.status_code}")

            if response.status_code in (429, 403):
                print(f"Retryable status for params: {params}")
                print("Response body:", response.text)
                time.sleep(2 ** attempt)
                continue

            if not response.ok:
                print("Response body:", response.text)
                response.raise_for_status()

            return response.json(), response.status_code

        except requests.exceptions.Timeout:
            last_error = f"Timeout for params: {params}"
            print(last_error)
            if attempt == 2:
                raise Exception(last_error)
            time.sleep(2 ** attempt)

        except requests.exceptions.RequestException as e:
            last_error = f"Request failed for params: {params}. Error: {e}"
            print(last_error)

            # Print server response if available
            if "response" in locals() and response is not None:
                print("Status code:", response.status_code)
                print("Response body:", response.text)

            if attempt == 2:
                raise Exception(last_error)

            time.sleep(2 ** attempt)

    raise Exception(f"Weather API failed after retries for params: {params}. Last error: {last_error}")

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
            weather_kind="historical_backfill",
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

    weather_historical_df = spark.createDataFrame(rows)
    (
        weather_historical_df.write
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
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation,wind_speed_10m",
            "start_date":start_date,
            "end_date":end_date,
            "timezone": "UTC"
            }

        print(f"Fetching historical weather for {airport_code} ({lat}, {lon})")

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