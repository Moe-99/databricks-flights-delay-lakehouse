# Flight Delay & Weather Analytics Platform

<img width="788" height="571" alt="Flight-delay-lakehouse-architecture drawio" src="https://github.com/user-attachments/assets/f3990518-5040-4637-9743-8880e87a132c" />

## Architecture Overview

This project is an end-to-end data platform built on Databricks using the Medallion architecture (Bronze → Silver → Gold).

It started as a simple API ingestion pipeline, but was expanded into a full workflow that includes ingestion, transformation, modeling, orchestration, and a dashboard layer.

Data is pulled from external APIs, stored as raw Delta tables, transformed using PySpark, and then aggregated into analytical tables used for reporting.

The pipeline is scheduled using Databricks Jobs, so everything runs automatically without manual execution.

## System Components

The pipeline consists of four major components:

- Data Sources

- Data Ingestion

- Medallion Data Layers (Bronze, Silver, Gold)

- Orchestration & Scheduling

- Consumption layer (dashboard)


## Data Sources

The project uses three external data sources:

### Flight Data API

Flight information is retrieved from the AviationStack API, which provides real-time flight metadata including:

- airline information

- flight numbers

- departure and arrival airports

- scheduled timestamps

- delay information

### Weather Data API

Weather information is retrieved from the Open-Meteo API, providing hourly weather measurements for airport locations including:

- air temperature

- precipitation

- wind speed

Two types of weather ingestion are implemented:

- Forecast ingestion for hourly operational monitoring

- Historical ingestion for aligning weather data with flight timestamps

### Airport Dataset

Airport metadata is sourced from the OurAirports open dataset, which provides information such as:

- airport identifiers (IATA / ICAO)

- geographic coordinates

- airport name

- country and region

This dataset is used to enrich flight and weather data with airport metadata.

A filtered subset of airports is used in the pipeline to control data volume and stay within API limits. This selection is based on region (Europe), airport type, and availability of IATA codes.

## Medallion Architecture

The pipeline follows the Databricks Medallion architecture, which organizes data into progressively refined layers.

Data Sources
     ↓
Bronze Layer (Raw Data)
     ↓
Silver Layer (Clean & Structured Data)
     ↓
Gold Layer (Analytical Tables)

Each layer has a specific responsibility within the pipeline.

### Bronze Layer – Raw Data

The Bronze layer stores raw ingested data exactly as it is received from the source systems.

Characteristics of this layer:

- Minimal transformation

- Raw API responses preserved

- Data stored in Delta tables

- Designed for traceability and debugging

- API responses are stored as JSON strings to preserve the original structure of the data. This allows the pipeline to reprocess historical data if transformations change in the future.

- Bronze ingestion is implemented using PySpark notebooks.

### Silver Layer – Cleaned & Structured Data

The Silver layer transforms raw data into structured datasets suitable for analysis.

Transformations performed in this layer include:

- Parsing JSON responses

- Flattening nested structures

- Exploding arrays into rows

- Standardizing column names

- Handling null / empty values

- Converting timestamps

## Basic data validation

PySpark is used to convert semi-structured API responses into structured tabular datasets.

The Silver layer creates normalized datasets representing:

- flights

- airport metadata

- hourly weather observations

## Gold Layer – Analytical Data

The Gold layer produces analytics-ready datasets designed for reporting and insights.

These datasets aggregate and enrich information from the Silver layer to support business analysis.

Examples of analytical datasets include:

- airport delay summaries

- airline delay performance

- flight-level delay metrics

- enriched flight records combined with weather data

These datasets are primarily created using SQL transformations.

This is also where business logic is defined, for example:

- what counts as a delayed flight

- how delay rates are calculated

- how weather is joined to flights

## Orchestration and Automation

The pipeline is orchestrated using Databricks Jobs.

Instead of one large job, the workflow is split into separate pipelines based on responsibility.

### Flights Pipeline
Runs every 12 hours.

Handles:

- flight API ingestion

- Silver flights transformation

- Gold delay summary tables

The schedule was chosen to avoid API rate limits.

### Weather Pipeline
Runs once per day.

Handles:

- forecast ingestion

- recent historical ingestion

- Silver weather transformation

- Gold flight-weather enrichment

### Archive Backfill Pipeline (Manual)
Used for historical weather backfills.

This job is not scheduled and is triggered manually when needed.

After backfill:

- Silver weather is rebuilt

- Gold enrichment tables are refreshed

## Consumption Layer – Dashboard
The final layer of the pipeline is the analytics dashboard, built using Databricks SQL.

This layer consumes Gold tables and presents the data in a format suitable for analysis.

The dashboard includes:

- KPI metrics (total flights, delay rate, on-time rate)

- Delay breakdown by airline and airport

- Weather impact analysis (wind and precipitation)

- Flight volume trends over time

## Storage Layer
All data is stored using Delta Lake.

This provides:

- ACID transactions

- Schema enforcement

- Scalable storage

- Reliable overwrite operations

Bronze acts as the source of truth, while Silver and Gold are rebuilt from it as needed.

## Technology Stack

- Databricks Lakehouse

- PySpark

- SQL

- Delta Lake

- REST APIs

- Databricks Jobs (Workflows)

## Summary
This project demonstrates a complete data workflow, from ingestion to analytics.

It covers:

- API-based data ingestion

- Handling semi-structured data

- Layered transformations (Bronze → Silver → Gold)

- Building analytical datasets

- Orchestrating scheduled pipelines

- Exposing results through a dashboard

The focus was on building something practical and explainable, while working within real-world constraints like API rate limits.
