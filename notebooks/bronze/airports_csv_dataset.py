import requests

from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

CSV_URL = "https://ourairports.com/data/airports.csv"
VOLUME_PATH = "/Volumes/dev_project/flight_delay_lakehouse/raw_files/airports.csv"
BRONZE_TABLE = "dev_project.flight_delay_lakehouse.bronze_airports_raw"


def download_csv(csv_url: str, volume_path: str):
    try:
        response = requests.get(csv_url, timeout=60)
        response.raise_for_status()

        with open(volume_path, "wb") as f:
            f.write(response.content)

        print("CSV successfully downloaded")
        print("Status:", response.status_code)
        print("Bytes downloaded:", len(response.content))
        print("Saved to:", volume_path)

    except requests.exceptions.Timeout:
        raise Exception("Download failed: request timed out")

    except requests.exceptions.HTTPError as e:
        raise Exception(f"Download failed: HTTP error {e}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Download failed: request error {e}")


def get_airports_schema() -> StructType:
    return StructType([
        StructField("id", IntegerType(), True),
        StructField("ident", StringType(), True),
        StructField("type", StringType(), True),
        StructField("name", StringType(), True),
        StructField("latitude_deg", DoubleType(), True),
        StructField("longitude_deg", DoubleType(), True),
        StructField("elevation_ft", IntegerType(), True),
        StructField("continent", StringType(), True),
        StructField("iso_country", StringType(), True),
        StructField("iso_region", StringType(), True),
        StructField("municipality", StringType(), True),
        StructField("scheduled_service", StringType(), True),
        StructField("icao_code", StringType(), True),
        StructField("iata_code", StringType(), True),
        StructField("gps_code", StringType(), True),
        StructField("local_code", StringType(), True),
        StructField("home_link", StringType(), True),
        StructField("wikipedia_link", StringType(), True),
        StructField("keywords", StringType(), True),
    ])


def read_airports_csv(volume_path: str, csv_url: str, schema: StructType):
    airports_df = (
        spark.read
        .schema(schema)
        .option("header", True)
        .csv(volume_path)
        .withColumn("ingested_at", current_timestamp())
        .withColumn("source_system", lit("ourairports"))
        .withColumn("source_url", lit(csv_url))
    )

    return airports_df


def write_bronze_airports(airports_df):
    row_count = airports_df.count()
    print(f"Writing {row_count} rows to bronze table")

    (
        airports_df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(BRONZE_TABLE)
    )


def main():
    download_csv(CSV_URL, VOLUME_PATH)
    schema = get_airports_schema()
    airports_df = read_airports_csv(VOLUME_PATH, CSV_URL, schema)
    write_bronze_airports(airports_df)
    print(f"Bronze airports table loaded successfully into {BRONZE_TABLE}")


main()
