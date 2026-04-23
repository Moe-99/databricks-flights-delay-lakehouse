# **Flight Delay & Weather Analytics Platform**
## Overview

Flight delays cost airlines and passengers billions each year. This project explores whether weather conditions have a measurable impact on flight delays.

Instead of just analyzing a dataset, I built a full end-to-end data platform on Databricks to ingest, process, and analyze flight and weather data.

The pipeline follows a lakehouse architecture (Bronze → Silver → Gold) and is fully orchestrated using scheduled workflows. The final output is a dashboard that allows analysis of delays across airlines, airports, and weather conditions.

The system ingests data from multiple sources, processes it through a Bronze–Silver–Gold Lakehouse architecture, and produces analytical tables designed for reporting and decision-making.

The pipeline integrates flight data, weather data, and airport metadata, enabling analysis of flight delays across airports, airlines, and environmental conditions.

The pipeline is fully orchestrated and automated using Databricks Jobs, allowing scheduled ingestion and transformation workflows.

---
## What this project does
- Ingests flight, weather, and airport data from external sources

- Processes raw API data into structured datasets using PySpark

- Builds analytical tables using SQL

- Enriches flight records with weather conditions

- Runs automatically using Databricks Jobs

- Exposes results through a dashboard

## Architecture

<img width="788" height="571" alt="Flight-delay-lakehouse-architecture drawio" src="https://github.com/user-attachments/assets/f3990518-5040-4637-9743-8880e87a132c" />


The pipeline follows a **Medallion Architecture (Bronze → Silver → Gold)**.

- Bronze → raw ingestion

- Silver → cleaned and structured data

- Gold → analytics-ready tables

- Dashboard → consumption layer

---

## Data Sources
Flights API (AviationStack)
Provides:

- Flight identifiers

- Airline information

- Departure / arrival timestamps

- Delay metrics

⚠️ Note: The API has strict rate limits, so ingestion was scheduled every 12 hours.

---

## Weather API (Open-Meteo)
Provides hourly data:

- Temperature

- Precipitation

- Wind speed

- Used to align weather conditions with flight departure times.

---

## Airports Dataset
- CSV dataset providing:

- Airport metadata

- Geographic coordinates

- IATA codes

---

## Airport Selection Strategy
The pipeline does not use all airports.

Instead, a filtered subset of **50** European airports is used.

Selection criteria:

- Continent = Europe

- IATA code present

- Airport type = medium or large

This was done to:

- Reduce API usage

- Stay within rate limits

- Keep the dataset meaningful

- Ensure consistent results across runs

## Data Model
Bronze Layer (Raw)
Stores raw API responses with minimal transformation.

Tables:

- ronze_flights_raw

- bronze_weather_raw

- bronze_airports_raw

## Silver Layer (Structured)
Transforms raw data into usable tables.

Tables:

- silver_flights

- silver_weather_hourly

- silver_airports

Main transformations:

- JSON parsing

- Flattening nested fields

- Exploding weather arrays

- Timestamp normalization

## Gold Layer (Analytics)
Analytics-ready datasets used by the dashboard.

Tables:

- gold_airport_delay_summary

- gold_airline_delay_summary

- gold_flight_delay_summary

- gold_flight_weather_enriched

## Flight + Weather Enrichment
The main dataset joins flights with weather:

ON dep_airport_iata = airport_iata
AND date_trunc('hour', dep_scheduled_ts) = weather_ts
This allows analysis of how weather conditions relate to delays.

## Dashboard (Consumption Layer)
The final output is a Databricks SQL dashboard.

It includes:

- KPI overview (total flights, delay rate, on-time rate)

- Delay breakdown by airline and airport

- Weather impact analysis

- Flight volume trends over time

## Orchestration
The pipeline is automated using Databricks Workflows.

Each pipeline is broken into tasks with clear dependencies, allowing ingestion and transformations to run in the correct order.

Flights pipeline:
DAG:

<img width="607" height="279" alt="Screenshot 2026-04-23 184733" src="https://github.com/user-attachments/assets/71479aa4-63da-423a-adc3-7d6d09c079cd" />

Weather pipeline:
DAG:

<img width="620" height="202" alt="Screenshot 2026-04-23 184857" src="https://github.com/user-attachments/assets/be598a06-3a26-48af-87ae-20e5113f1467" />

Archive backfill
DAG:

<img width="615" height="133" alt="Screenshot 2026-04-23 184957" src="https://github.com/user-attachments/assets/0ce5e9b5-7b03-4d95-9016-933abc401292" />

## Flights Pipeline
- Runs every 12 hours:

- Flight ingestion

- Silver transformations

- Gold summaries

## Weather Pipeline
Runs daily:

- Forecast ingestion

- Historical ingestion

- Enrichment updates

## Backfill (Manual)
Used to load historical weather data when needed.# Lakehouse Data Model

## Technologies Used
- Databricks Lakehouse

- PySpark

- SQL

- Delta Lake

- REST APIs

- Databricks Jobs## Bronze Layer – Raw Data

## Example Questions Answered
- Which airports have the highest delay rates?

- Which airlines are most reliable?

- Does weather impact flight delays?

- How do delays change over time?

## Dashboard

The final output of the pipeline is a Databricks SQL dashboard.

It provides:

- KPI overview (total flights, delay rate, on-time rate)
- Delay breakdown by airline and airport
- Weather impact analysis
- Flight trends over time

<img width="1168" height="1154" alt="screencapture-dbc-7c43730a-2968-cloud-databricks-sql-dashboardsv3-01f13d8974ba1dc78f3d8ab011b9ca33-2026-04-23-18_59_58" src="https://github.com/user-attachments/assets/d37047c6-15e8-405b-bc21-1867baa060f1" />

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

## Challenges
API rate limits required careful scheduling

aligning weather timestamps with flight data

handling semi-structured JSON data

keeping transformations simple while avoiding duplicates

---

## Future Improvements
richer historical flight data

better weather categorization (heavy rain, strong wind)

data quality monitoring

CI/CD for pipeline deployment

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





