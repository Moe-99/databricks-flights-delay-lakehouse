from dotenv import load_dotenv
import os
import requests
import json
from pyspark.sql import Row
from datetime import datetime
import uuid


load_dotenv() 
API_KEY = os.environ.get("AVIATIONSTACK_KEY")
BASE_URL = "https://api.aviationstack.com/v1/flights"
airports = ['AMS', 'LHR', 'JFK']
run_id = str(uuid.uuid4())
ingested_at = datetime.utcnow()

rows =[]
for airport in airports:
    params = {
        "access_key": API_KEY,
        "dep_iata": airport,
        "limit":50
    }

    r = requests.get(BASE_URL, params = params, timeout = 30)
    r.raise_for_status()
    payload = r.json()
    for item in payload.get('data', []):
        rows.append(
            Row(
                run_id = run_id,
                ingested_at = ingested_at,
                source = 'aviationstack',
                query_params = json.dumps(params),
                raw_record_json = json.dumps(item)
            )
        )
df = spark.createDataFrame(rows)
(df.write
    .format('delta')
    .mode('append')
    .saveAsTable('dev_project.flight_delay_lakehouse.bronze_flights_raw'))
