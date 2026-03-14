# Data Model

This document describes the logical data model used in the Flight Delay Lakehouse pipeline.

The system follows a **Medallion Architecture** consisting of Bronze, Silver, and Gold layers.

---

# Bronze Layer (Raw Data)

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

# Silver Layer (Clean & Structured Data)

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

---

### silver_airports

| Column | Description |
|------|-------------|
| airport_iata | Airport IATA code |
| airport_name | Airport name |
| country_code | Country |
| latitude | Latitude coordinate |
| longitude | Longitude coordinate |

---

# Gold Layer (Analytics Tables)

The Gold layer contains **aggregated and business-ready tables** optimized for analytics and reporting.

| Table | Description |
|------|-------------|
| gold_airport_delay_summary | Delay metrics per airport per day |
| gold_airline_delay_summary | Delay metrics per airline |
| gold_flight_delay_summary | Delay metrics per flight number |
| gold_flight_weather_enriched | Flight records enriched with weather conditions |

---

# Example Data Integration

The `gold_flight_weather_enriched` table combines flight data with weather conditions at the time of departure.

### Join Logic
silver_flights
JOIN silver_weather_hourly

### Join conditions:
flight.dep_airport_iata = weather.airport_iata
AND date_trunc('hour', dep_scheduled_ts) = weather.weather_ts

![weather_enrichment_data_model.png](https://github.com/Moe-99/databricks-flights-delay-lakehouse/blob/master/diagrams/weather_enrichment_data_model.png)


This produces a dataset where each flight record contains:

- departure information
- delay metrics
- weather conditions at departure time

---

# Fact and Dimension Tables

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

# Summary

This data model enables analysis of:

- airport operational performance
- airline reliability
- delay trends over time
- weather impact on flight delays

The layered architecture ensures data is:

- traceable
- scalable
- analytics-ready


