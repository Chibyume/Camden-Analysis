import snowflake.connector
import pandas as pd

SNOWFLAKE_USER = "ENTER USERNAME HERE"
SNOWFLAKE_PASSWORD = "ENTER PASSWORD HERE"
SNOWFLAKE_ACCOUNT = "kac12786.us-east-1"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "CAMDEN_ANALYSIS"
SNOWFLAKE_SCHEMA = "PUBLIC"

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)

cursor = conn.cursor()
cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
cursor.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")

# --- dimension tables ---

# zip code info -- city, county, state
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_location (
        zip_code  VARCHAR(10) PRIMARY KEY,
        city      VARCHAR(50),
        county    VARCHAR(50),
        state     VARCHAR(20)
    )
""")

# year dimension -- keeps the fact table clean
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_year (
        year_id       NUMBER PRIMARY KEY,
        year          NUMBER,
        survey_label  VARCHAR(50)
    )
""")

# --- fact table ---

# one row per zip per year, all the metrics
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_socioeconomic (
        fact_id           NUMBER AUTOINCREMENT PRIMARY KEY,
        zip_code          VARCHAR(10),
        year_id           NUMBER,
        median_income     NUMBER,
        poverty_rate      FLOAT,
        unemployment_rate FLOAT,
        hs_grad_rate      FLOAT,
        uninsured_rate    FLOAT,
        snap_rate         FLOAT,
        median_gross_rent NUMBER,
        no_vehicle_pct    FLOAT,
        pct_hispanic      FLOAT,
        pct_white         FLOAT,
        pct_black         FLOAT
    )
""")

print("tables created")

# --- load dimension tables ---

# zip location info
zip_info = [
    ("08102", "Camden", "Camden County", "New Jersey"),
    ("08103", "Camden", "Camden County", "New Jersey"),
    ("08104", "Camden", "Camden County", "New Jersey"),
    ("08105", "Camden", "Camden County", "New Jersey"),
    ("08106", "Haddon Township", "Camden County", "New Jersey"),
]

for zip_code, city, county, state in zip_info:
    cursor.execute("""
        MERGE INTO dim_location USING (SELECT %s AS zip_code) src
        ON dim_location.zip_code = src.zip_code
        WHEN NOT MATCHED THEN INSERT (zip_code, city, county, state)
        VALUES (%s, %s, %s, %s)
    """, (zip_code, zip_code, city, county, state))

print("dim_location loaded")

# years we pulled
year_data = [
    (2019, 2019, "ACS 5-Year 2019"),
    (2021, 2021, "ACS 5-Year 2021"),
    (2022, 2022, "ACS 5-Year 2022"),
]

for year_id, year, label in year_data:
    cursor.execute("""
        MERGE INTO dim_year USING (SELECT %s AS year_id) src
        ON dim_year.year_id = src.year_id
        WHEN NOT MATCHED THEN INSERT (year_id, year, survey_label)
        VALUES (%s, %s, %s)
    """, (year_id, year_id, year, label))

print("dim_year loaded")

# --- load fact table ---

df = pd.read_csv(r"C:\Users\aweso\OneDrive\Desktop\Camden_Analysis\camden_data.csv")


def clean(val, cast=float):
    if pd.isna(val):
        return None
    return cast(val)


for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO fact_socioeconomic
            (zip_code, year_id, median_income, poverty_rate, unemployment_rate,
             hs_grad_rate, uninsured_rate, snap_rate, median_gross_rent,
             no_vehicle_pct, pct_hispanic, pct_white, pct_black)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["zip_code"],
        int(row["year"]),
        clean(row["median_income"], int),
        clean(row["poverty_rate"]),
        clean(row["unemployment_rate"]),
        clean(row["hs_grad_rate"]),
        clean(row["uninsured_rate"]),
        clean(row["snap_rate"]),
        clean(row["median_gross_rent"], int),
        clean(row["no_vehicle_pct"]),
        clean(row["pct_hispanic"]),
        clean(row["pct_white"]),
        clean(row["pct_black"]),
    ))

conn.commit()
print(f"fact_socioeconomic loaded: {len(df)} rows")

cursor.close()
conn.close()
