# Data Model

This document describes the logical data model used in the Flight Delay Lakehouse pipeline.

The system follows a **Medallion Architecture** consisting of Bronze, Silver, and Gold layers.

---

## Airport Selection Strategy

The project does not use all available airports from the source dataset.

Instead, a filtered subset of airports was selected to keep the pipeline realistic and manageable.

### Step 1 – Candidate Airports

A candidate set of airports is created from the raw airport dataset using the following filters:

- continent = 'EU'
- IATA code is not null
- airport type in ('medium_airport', 'large_airport')

This removes very small airports and ensures that only operationally relevant airports are included.

Duplicates are removed based on the airport IATA code.

---

### Step 2 – Controlled Airport Set

From the candidate set, a fixed list of 50 airports is selected.

This list is stored in a separate table:

- `control_selected_airports`

This table acts as a control layer for the pipeline.

Only these airports are used for:

- flight ingestion
- weather ingestion
- downstream transformations

---

### Why this approach?

Using a controlled airport list helps:

- avoid unnecessary API calls
- stay within API rate limits
- keep the dataset consistent across runs
- make analysis more focused and meaningful

This also makes the pipeline easier to debug and reproduce.

## Bronze Layer (Raw Data)

The Bronze layer stores **raw ingested data** from external sources with minimal transformation.

These tables preserve the original structure of the source data for traceability and debugging.

| Table | Description |
|------|-------------|
| bronze_flights_raw | Raw JSON responses from the AviationStack Flights API |
| bronze_weather_raw | Raw JSON responses from the Open-Meteo Weather API |
| bronze_airports_raw | Airport metadata loaded from a CSV dataset |

Key characteristics:

- append-only ingestion
- original JSON preserved
- ingestion metadata added (`run_id`, `ingested_at`, `source`)

---

## Silver Layer (Clean & Structured Data)

The Silver layer contains **cleaned, normalized, and structured datasets** derived from Bronze tables.

Transformations performed:

- JSON parsing
- flattening nested fields
- exploding weather arrays into hourly records
- timestamp normalization
- column standardization
- data quality checks

| Table | Description |
|------|-------------|
| silver_flights | Structured flight records |
| silver_weather_hourly | Hourly weather observations per airport |
| silver_airports | Clean airport reference data |

Example structure:

### silver_flights

| Column | Description |
|------|-------------|
| flight_iata | Flight identifier |
| airline_name | Airline operating the flight |
| dep_airport_iata | Departure airport |
| arr_airport_iata | Arrival airport |
| dep_scheduled_ts | Scheduled departure timestamp |
| dep_delay_minutes | Departure delay in minutes |
| ingested_at | Data ingestion timestamp |

Table sample:

<img width="679" height="382" alt="Screenshot 2026-04-23 180901" src="https://github.com/user-attachments/assets/949b9be0-d64d-4ea4-a54f-3181fd1e1f1e" />

---

### silver_weather_hourly

| Column | Description |
|------|-------------|
| airport_iata | Airport code |
| weather_ts | Weather observation timestamp |
| air_temperature | Temperature (°C) |
| precipitation | Precipitation (mm) |
| wind_speed | Wind speed (km/h) |
| weather_kind | Forecast or historical observation |

Table sample:

<img width="680" height="379" alt="Screenshot 2026-04-23 181125" src="https://github.com/user-attachments/assets/24bdacfe-0092-4436-9f8e-5eb5a75adb52" />

---

### silver_airports

| Column | Description |
|------|-------------|
| airport_iata | Airport IATA code |
| airport_name | Airport name |
| country_code | Country |
| latitude | Latitude coordinate |
| longitude | Longitude coordinate |

Table sample:

<img width="683" height="380" alt="Screenshot 2026-04-23 181255" src="https://github.com/user-attachments/assets/c196e719-8d3b-4a5f-af16-6d7ad608ff1c" />

---

## Gold Layer (Analytics Tables)

The Gold layer contains **aggregated and business-ready tables** optimized for analytics and reporting.

| Table | Description |
|------|-------------|
| gold_airport_delay_summary | Delay metrics per airport per day |
| gold_airline_delay_summary | Delay metrics per airline |
| gold_flight_delay_summary | Delay metrics per flight number |
| gold_flight_weather_enriched | Flight records enriched with weather conditions |

---

## Example Data Integration

The `gold_flight_weather_enriched` table combines flight data with weather conditions at the time of departure.

### Join Logic
silver_flights
JOIN silver_weather_hourly

### Join conditions:
flight.dep_airport_iata = weather.airport_iata
AND date_trunc('hour', dep_scheduled_ts) = weather.weather_ts

![weather_enrichment_data_model.png](https://github.com/Moe-99/databricks-flights-delay-lakehouse/blob/master/diagrams/weather_enrichment_data_model.png)

Table sample:

<img width="680" height="380" alt="Screenshot 2026-04-23 181656" src="https://github.com/user-attachments/assets/20013655-f829-43b8-96af-42f646d70f0e" />


This produces a dataset where each flight record contains:

- departure information
- delay metrics
- weather conditions at departure time

---

## Fact and Dimension Tables

The model follows a **fact-dimension pattern**.

### Fact Tables

| Table |
|------|
silver_flights

This table contains **event-level flight records**.

---

### Dimension Tables

| Table |
|------|
silver_airports  
silver_weather_hourly

These tables provide **descriptive and environmental context** for flight events.

---

# Grain of the Data

| Table | Grain |
|------|------|
silver_flights | one row per flight event |
silver_weather_hourly | one row per airport per hour |
gold_airport_delay_summary | one row per airport per day |
gold_airline_delay_summary | one row per airline |
gold_flight_delay_summary | one row per flight per day |
gold_flight_weather_enriched | one row per flight |

---

## Summary

This data model enables analysis of:

- airport operational performance
- airline reliability
- delay trends over time
- weather impact on flight delays

The layered architecture ensures data is:

- traceable
- scalable
- analytics-ready


