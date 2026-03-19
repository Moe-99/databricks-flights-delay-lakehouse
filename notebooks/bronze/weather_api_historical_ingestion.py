import requests, json, uuid, time
from pyspark.sql.functions import col
from datetime import datetime, timezone, timedelta
from pyspark.sql import Row

dbutils.widgets.text("target_date", "")
target_date = dbutils.widgets.get("target_date").strip()

if not target_date:
    target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_weather_data(lat, lon,params):
    for attempt in range(3):
        r = requests.get(WEATHER_URL, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise Exception(f"Weather API failed for {lon}, {lat} after 3 retries")

def to_bronze_record(payload, airport_iata, lat, lon, params):
    return Row(
        run_id=str(uuid.uuid4()),
        ingested_at=datetime.now(timezone.utc),
        source="open-meteo",
        airport_iata = airport_iata,
        longitude = lon,
        latitude = lat,
        weather_kind="historical",
        query_params=json.dumps(params),
        raw_response_json=json.dumps(payload)
    )

def store(records):
    weather_df_historical = spark.createDataFrame(records)
    weather_df_historical.write.mode("append").format("delta").saveAsTable("dev_project.flight_delay_lakehouse.bronze_weather_raw")

def main():
    AIRPORTS = ["AMS", "LHR", "JFK"]
    airports_df = (
    spark.table("dev_project.flight_delay_lakehouse.bronze_airports_raw")
    .select("iata_code", "latitude_deg", "longitude_deg")
    .where(col("iata_code").isin(AIRPORTS)))

    airport_rows = airports_df.collect()
    rows = []
    for a in airport_rows:
        airport = a["iata_code"]
        lat = float(a["latitude_deg"])
        lon = float(a["longitude_deg"])
        
        params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": target_date,
        "end_date": target_date,
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "UTC"}
        payload = fetch_weather_data(lat,lon,params)
        records = to_bronze_record(payload,airport,lat,lon,params)
        rows.append(records)

    store(rows)
main()

     




