# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

import time
from datetime import datetime, timezone
import json
import uuid
import requests
from pyspark.sql import Row

# COMMAND ----------

# MAGIC %md
# MAGIC ## Constants

# COMMAND ----------

API_KEY = "a6fbc8e27bc8c4c70342f493c04b1b0a"
BASE_URL = "https://api.aviationstack.com/v1/flights"
SELECTED_AIRPORTS_TABLE = "dev_project.flight_delay_lakehouse.control_selected_airports"
BRONZE_TABLE = "dev_project.flight_delay_lakehouse.bronze_flights_raw"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get selected airports

# COMMAND ----------

def get_selected_airport_codes():
    selected_airports_df = spark.table(SELECTED_AIRPORTS_TABLE)

    airport_codes = [
        row["airport_code"]
        for row in selected_airports_df.select("airport_code").collect()
    ]
    return airport_codes

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chunk list

# COMMAND ----------

def chunk_list(items: list, chunk_size: int):
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch_flights

# COMMAND ----------

def fetch_flights(params: dict):
    for attempt in range(3):
        try:
            response = requests.get(BASE_URL, params=params, timeout=120)

            if response.status_code in (429, 403):
                print(f"Attempt {attempt + 1}: status {response.status_code} for {params['dep_iata']}, retrying...")
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response.json(), response.status_code
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1}: timeout for {params['dep_iata']}")
            if attempt == 2:
                raise Exception(f"Flights API timed out after 3 attempts for params: {params}")
            time.sleep(2 ** attempt)

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: request error for {params['dep_iata']}: {e}")
            if attempt == 2:
                raise Exception(f"Flights API request failed after 3 attempts for params: {params}. Error: {e}")
            time.sleep(2 ** attempt)

    raise Exception(f"Flights API failed after retries for params: {params}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## To bronze rows

# COMMAND ----------

def to_bronze_rows(payload: dict, params: dict, airport_code: str) -> list:
    rows = []
    ingested_at = datetime.now(timezone.utc).isoformat()
    run_id = str(uuid.uuid4())
    for item in payload.get("data", []):
        rows.append(
            Row(
                run_id=run_id,
                ingested_at=ingested_at,
                source="aviationstack",
                airport_code=airport_code,
                query_params=json.dumps(params),
                raw_record_json=json.dumps(item)
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

    flights_df = spark.createDataFrame(rows)

    (
        flights_df.write
        .format("delta")
        .mode("append")
        .saveAsTable(BRONZE_TABLE)
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main pipeline

# COMMAND ----------

def main():
    if not API_KEY:
        raise Exception("Missing API key")

    airport_codes = get_selected_airport_codes()
    airport_batches = list(chunk_list(airport_codes, 10))

    print(f"Total airports: {len(airport_codes)}")
    print(f"Total batches: {len(airport_batches)}")
    for batch_number, airport_batch in enumerate(airport_batches, start=1):
        print(f"\n--- Processing batch {batch_number}/{len(airport_batches)} ({len(airport_batch)} airports) ---")

        for airport_code in airport_batch:
            print(f"\nFetching flights for airport: {airport_code}")

            params = {
                "access_key": API_KEY,
                "dep_iata": airport_code,
                "limit": 10
            }

            payload, status_code = fetch_flights(params)

            record_count = len(payload.get("data", []))
            print(f"Status code: {status_code}")
            print(f"Records returned: {record_count}")
            if record_count > 0:
                print("Sample raw record:")
                print(json.dumps(payload["data"][0], indent=2)[:1000])

            rows = to_bronze_rows(payload, params, airport_code)
            write_to_delta(rows)

            time.sleep(2)

        print(f"Finished batch {batch_number}")
        time.sleep(5)
    

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run pipeline

# COMMAND ----------

main()