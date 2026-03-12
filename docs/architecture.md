# Flight Delay Lakehouse Architecture

<img width="788" height="571" alt="Flight-delay-lakehouse-architecture drawio" src="https://github.com/user-attachments/assets/f3990518-5040-4637-9743-8880e87a132c" />

## Architecture Overview

This project implements an end-to-end Databricks Lakehouse pipeline using the Medallion architecture (Bronze → Silver → Gold) to process flight and weather data.

The system ingests data from external APIs and open datasets, stores raw data in Delta tables, transforms it into structured datasets using PySpark, and produces analytical datasets for reporting.

The pipeline is orchestrated using Databricks Jobs, enabling automated data ingestion and transformation workflows.

## System Components

The pipeline consists of four major components:

- Data Sources

- Data Ingestion

- Medallion Data Layers

- Orchestration & Scheduling

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

- enriched flight records combined with weather data

These datasets are primarily created using SQL transformations.

## Orchestration and Automation

The pipeline is orchestrated using Databricks Jobs, which automate execution of the ingestion and transformation workflows.

Two job pipelines are implemented:

Hourly Pipeline

Runs every hour to process operational data.

### Tasks include:

- Flight API ingestion

- Weather forecast ingestion

- Silver layer transformations

- Gold delay summary tables

### Daily Historical Pipeline

Runs once per day to align weather data with historical flight records.

Tasks include:

- Historical weather ingestion

- Silver weather transformation

- Flight-weather enrichment table

### Scheduling

The pipelines are scheduled using Databricks job scheduling:

- Hourly pipeline: runs every hour

- Daily pipeline: runs once per day

This ensures the system continuously ingests new data while maintaining historical alignment between flight and weather datasets.

## Storage Layer

All datasets are stored using Delta Lake, which provides:

- ACID transactions

- schema enforcement

- scalable storage

- time travel capabilities

- Delta tables enable reliable incremental processing within the lakehouse architecture.

## Technology Stack

The project uses the following technologies:

- Databricks Lakehouse

- PySpark

- SQL

- Delta Lake

- REST APIs

- Databricks Jobs (Orchestration)

## Summary

This architecture demonstrates a scalable lakehouse pipeline capable of:

- ingesting external API data

- transforming semi-structured data

- building analytical datasets

- orchestrating automated workflows

The design follows modern data engineering best practices by combining the Medallion architecture, Delta Lake storage, and Databricks orchestration tools.
