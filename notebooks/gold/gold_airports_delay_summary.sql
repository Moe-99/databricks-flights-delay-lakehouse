-- Databricks notebook source
CREATE OR REPLACE TABLE dev_project.flight_delay_lakehouse.gold_airport_delay_summary AS 
SELECT
  f. dep_airport_iata,
  a.airport_name,
  a.country,
  a.airport_type,
  CAST(f.dep_scheduled_ts AS DATE) AS flight_date,
  COUNT(*) AS total_flights,
  SUM(CASE WHEN f.dep_delay_minutes >= 15 THEN 1 ELSE 0 END) AS delayed_flights,
  SUM(CASE WHEN f.dep_delay_minutes IS NOT NULL THEN 1 ELSE 0 END) AS flights_with_known_delay,
  SUM(CASE WHEN f.dep_delay_minutes IS NULL OR f.dep_delay_minutes < 15 THEN 1 ELSE 0 END) AS on_time_flights,
  ROUND(AVG(f.dep_delay_minutes), 2) AS avg_dep_delay_minutes,
  ROUND(
  100.0 * SUM(CASE WHEN f.dep_delay_minutes IS NULL OR f.dep_delay_minutes < 15 THEN 1 ELSE 0 END)
  / NULLIF(COUNT(*), 0),
  2
) AS on_time_rate,
  ROUND(
  100.0 * SUM(CASE WHEN f.dep_delay_minutes >= 15 THEN 1 ELSE 0 END)
  / NULLIF(COUNT(*), 0),
  2
) AS delay_rate
FROM dev_project.flight_delay_lakehouse.silver_flights f 
LEFT JOIN dev_project.flight_delay_lakehouse.silver_airports a 
ON f.dep_airport_iata = a.iata_code
GROUP BY 
  dep_airport_iata,
  CAST(dep_scheduled_ts AS DATE),
  a.airport_name,
  a.country,
  a.airport_type




