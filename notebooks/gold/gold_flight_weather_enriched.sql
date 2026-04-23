-- Databricks notebook source
CREATE OR REPLACE TABLE dev_project.flight_delay_lakehouse.gold_flight_weather_enriched
USING DELTA
PARTITIONED BY (flight_date)
AS
SELECT
  f.flight_iata,
  f.flight_number,
  f.airline_name,
  f.airline_iata,
  f.flight_status,

  f.dep_airport_iata,
  a.airport_name,
  a.airport_type,
  a.country,

  f.arr_airport_iata,

  CAST(f.dep_scheduled_ts AS DATE) AS flight_date,
  f.dep_scheduled_ts,
  date_trunc('hour', f.dep_scheduled_ts) AS dep_hour,
  f.dep_delay_minutes,

  w.air_temperature_2m_c,
  w.precipitation_mm,
  w.wind_speed_10m_kmh,
  w.weather_kind,

  CASE
    WHEN f.dep_delay_minutes >= 15 THEN 1
    ELSE 0
  END AS is_delayed,

  CASE
    WHEN f.dep_delay_minutes IS NULL OR f.dep_delay_minutes < 15 THEN 1
    ELSE 0
  END AS is_on_time,

  CASE
    WHEN w.precipitation_mm = 0 THEN 'no_precipitation'
    WHEN w.precipitation_mm < 1 THEN 'light_precipitation'
    WHEN w.precipitation_mm < 5 THEN 'moderate_precipitation'
    ELSE 'heavy_precipitation'
  END AS precipitation_bucket,

  CASE
    WHEN w.wind_speed_10m_kmh < 20 THEN 'low_wind'
    WHEN w.wind_speed_10m_kmh < 40 THEN 'moderate_wind'
    ELSE 'high_wind'
  END AS wind_bucket

FROM dev_project.flight_delay_lakehouse.silver_flights f
LEFT JOIN dev_project.flight_delay_lakehouse.silver_weather_hourly w
  ON f.dep_airport_iata = w.airport_code
 AND date_trunc('hour', f.dep_scheduled_ts) = w.weather_ts
LEFT JOIN dev_project.flight_delay_lakehouse.silver_airports a
  ON f.dep_airport_iata = a.iata_code

-- COMMAND ----------

SELECT * FROM dev_project.flight_delay_lakehouse.gold_airport_delay_summary