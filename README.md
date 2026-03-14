# Flight Delay Lakehouse Pipeline (Databricks)

## Overview

This project builds a **modern data engineering pipeline using Databricks and Delta Lake** to analyze flight delays and their relationship with weather conditions.

The system ingests data from multiple sources, processes it through a **Bronze–Silver–Gold Lakehouse architecture**, and produces analytical tables designed for reporting and decision-making.

The pipeline integrates **flight data, weather data, and airport metadata**, enabling analysis of flight delays across airports, airlines, and environmental conditions.

The pipeline is fully **orchestrated and automated using Databricks Jobs**, allowing scheduled ingestion and transformation workflows.

---

# Architecture


The pipeline follows a **Medallion Architecture (Bronze → Silver → Gold)**.


Automation and orchestration are implemented using **Databricks Jobs with scheduled workflows**.

---

# Data Sources

## Flights API
**Source:** AviationStack API  

Provides:

- flight identifiers
- airline information
- departure and arrival timestamps
- delay metrics

---

## Weather API
**Source:** Open-Meteo API  

Provides:

- hourly weather observations
- air temperature
- precipitation
- wind speed

Weather data is retrieved **per airport coordinates** to align with flight departure times.

---

## Airports Dataset

**Source:** Open airport dataset (CSV)

Provides:

- airport name
- country
- geographic coordinates
- IATA airport codes

---

# Lakehouse Data Model

## Bronze Layer – Raw Data

Purpose: **Store raw ingested data with minimal transformation**

### Tables

| Table | Description |
|------|-------------|
| `bronze_flights_raw` | Raw flight API responses stored as JSON |
| `bronze_weather_raw` | Raw weather API responses |
| `bronze_airports_raw` | Raw airport CSV dataset |

### Characteristics

- Raw JSON preserved for traceability
- Ingestion metadata added (`run_id`, `ingested_at`, `source`)
- Append-only ingestion
- No transformations applied

---

## Silver Layer – Clean & Structured Data

Purpose: **Transform raw data into structured datasets**

### Transformations

- JSON parsing
- exploding nested JSON structures
- timestamp normalization
- column standardization
- basic data quality validation

### Tables

| Table | Description |
|------|-------------|
| `silver_flights` | Structured flight records |
| `silver_weather_hourly` | Hourly weather observations per airport |
| `silver_airports` | Clean airport metadata |

### Example Transformation

Weather API responses contain **arrays of hourly values**.  
These arrays were **zipped and exploded** using PySpark to create **one row per hour per airport**.

---

## Gold Layer – Analytics Ready Tables

Purpose: **Provide business-ready aggregated datasets**

### Tables

| Table | Description |
|------|-------------|
| `gold_airport_delay_summary` | Flight delay metrics per airport per day |
| `gold_airline_delay_summary` | Delay metrics per airline |
| `gold_flight_delay_summary` | Delay metrics per flight number |
| `gold_flight_weather_enriched` | Flights enriched with weather conditions |

---

### Airport Delay Summary

`gold_airport_delay_summary`

Metrics:

- total flights
- delayed flights
- average departure delay
- on-time rate
- delay rate

This table is enriched with **airport metadata** (name and country).

---

### Airline Delay Summary

`gold_airline_delay_summary`

Metrics:

- total flights
- delayed flights
- average delay
- on-time rate

Provides insights into **airline operational performance**.

---

### Flight Delay Summary

`gold_flight_delay_summary`

Metrics per **flight number per day**:

- total flights
- delayed flights
- average delay
- on-time percentage

---

### Flight Weather Enrichment

`gold_flight_weather_enriched`

Flight records enriched with weather conditions at departure time.

Includes:

- air temperature
- precipitation
- wind speed
- weather observation timestamp

This table enables analysis of **weather impact on flight delays**.

---

# Orchestration & Automation

The pipeline is orchestrated using **Databricks Jobs**.

Two workflows were implemented.

---

## Hourly Pipeline

Runs every hour.

### Tasks

1. Flights API ingestion
2. Weather forecast ingestion
3. Silver flights transformation
4. Silver weather transformation
5. Gold airline delay summary
6. Gold airport delay summary
7. Gold flight delay summary

---

## Daily Pipeline

Runs once per day.

### Tasks

1. Historical weather ingestion
2. Silver weather processing
3. Gold flight weather enrichment

---

# Technologies Used

| Technology | Purpose |
|------------|--------|
| Python | API ingestion scripts |
| PySpark | Data transformation |
| SQL | Analytical aggregations |
| Databricks | Data platform and orchestration |
| Delta Lake | Storage layer with ACID transactions |
| REST APIs | Data ingestion |
| Medallion Architecture | Data modeling pattern |

---

# Engineering Concepts Demonstrated

- API data ingestion
- JSON schema parsing
- nested data processing
- PySpark transformations
- SQL analytics modeling
- Lakehouse architecture
- incremental pipelines
- Databricks orchestration
- scheduled automated workflows

---

# Example Insights

Using the Gold tables, analysts can answer questions such as:

- Which airports experience the most flight delays?
- Which airlines have the best on-time performance?
- Do weather conditions correlate with flight delays?
- How do precipitation or wind speeds impact departure delays?

---

# Future Improvements

Possible enhancements:

- weather condition bucketing analysis
- BI dashboard integration (Power BI / Tableau)
- data quality monitoring
- CI/CD pipeline integration
- Delta table partition optimization

---

```text
├── notebooks/
│   └── bronze/
│       └── airports_csv_dataset/
|       └── flights_api_ingestion/
|       └── airports_volume_to_delta_table/
|       └── weather_api_forecast_ingestion/
|       └── weather_api_historical_ingestion/ 
|   └── silver/
|       └── silver_airports/
|       └── silver_flights/
|       └── silver_weather_hourly/
|   └── gold/
|       └── gold_airline_delay_summary/
|       └── gold_flight_delay_summary/
|       └── gold_airport_delay_summary/
|       └── gold_flight_weather_enriched/
│ 
├── docs/
│   └── architecture.md/
|   └── data_model.md/
|──  diagrams/
|   └── Flight-delay-lakehouse-architecture.drawio
|   └── Flight-delay-lakehouse-architecture.drawio.png
|──  .gitignore
└── README.md





