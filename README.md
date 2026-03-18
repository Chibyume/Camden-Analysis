# Camden NJ Socioeconomic Analysis

I grew up in Camden, New Jersey. Everyone from there already knows what it looks like day to day, but I wanted to actually see the numbers behind it. I wanted to know how bad the poverty rate really was, how it compared ZIP code to ZIP code, and whether things had gotten better or worse over the past few years. This project was my way of answering those questions using real Census data and building something I could be proud of as a portfolio piece.

I am a Computer Science student at Rutgers University Camden studying data analytics. I built this project to practice working with a full data pipeline from scratch using tools I plan to use professionally.

---

## What I Built

I pulled socioeconomic data for five Camden County ZIP codes: 08102, 08103, 08104, 08105, and 08106. The data comes from the U.S. Census Bureau's American Community Survey across three years: 2019, 2021, and 2022. I picked those three years on purpose because 2019 is pre-COVID, 2021 is mid-recovery, and 2022 is the most recent available. I wanted to see if conditions actually improved or if the gap just stayed the same.

The pipeline works like this. Python pulls the data from the Census API and cleans it. Snowflake stores it. SQL analyzes it. Tableau visualizes it.

---

## Tech Stack

- Python with the requests and pandas libraries for data collection and cleaning
- Snowflake as the cloud data warehouse
- SQL for analysis queries
- Tableau for the interactive dashboard with a live Snowflake connection
- U.S. Census Bureau ACS 5-Year Estimates as the data source

---

## Data I Collected

For each ZIP code and each year I pulled the following:

- Median household income
- Poverty rate
- Unemployment rate
- High school graduation rate
- Uninsured rate
- SNAP participation
- Median gross rent
- Percentage of households with no vehicle
- Race and ethnicity breakdown

One thing worth knowing is that the Census API uses the number -666666666 as a placeholder when data is missing. The Python script detects that and removes it before anything gets loaded into Snowflake.

---

## Snowflake Schema

I used a star schema with three tables. The fact_socioeconomic table holds one row per ZIP code per year and stores all the metrics. The dim_location table stores ZIP code, city, county, and state. The dim_year table stores the year and survey label.

---

## SQL Analysis

The full queries are in analysis_queries.sql. Two of the more interesting ones are the rent burden calculation and the hardship index.

Rent burden shows what percentage of monthly income a household spends on rent. Since the Census reports income annually I divide by 12 to get the monthly figure first.

```sql
ROUND((median_gross_rent / NULLIF(median_income / 12, 0)) * 100, 1) AS rent_burden_pct
```

The hardship index is a composite score I created by averaging four deprivation indicators: poverty rate, unemployment rate, uninsured rate, and percentage of households with no vehicle. A higher score means more concentrated hardship.

```sql
ROUND((poverty_rate + unemployment_rate + uninsured_rate + no_vehicle_pct) / 4, 1) AS hardship_index
```

---

## Tableau Dashboard

The dashboard connects directly to Snowflake and includes eight visualizations. I also created two calculated fields inside Tableau itself.

Rent Burden percentage:
```
ROUND([MEDIAN_GROSS_RENT] / ([MEDIAN_INCOME] / 12) * 100, 1)
```

Hardship Index:
```
ROUND(([POVERTY_RATE] + [UNEMPLOYMENT_RATE] + [UNINSURED_RATE] + [NO_VEHICLE_PCT]) / 4, 1)
```

The most telling visualization is the socioeconomic heatmap at the top of the dashboard. It shows all five ZIP codes across five metrics on a red to green color scale. ZIP code 08106 is green across every single column. The other four ZIP codes are almost entirely red. That one chart summarizes the entire project better than anything else.

---

## Key Findings

08106 is a suburban ZIP code that shares Camden County but looks nothing like the core city ZIP codes statistically. The median income in 08106 is $93,670. In 08102 it is $30,679. That is a gap of nearly $63,000 within the same county. The poverty rate in core Camden ZIP codes ranges from 30 to 47 percent compared to 3.5 percent in 08106. Every metric, unemployment, uninsured rate, access to transportation, and education level, breaks along that same line.

The trend data from 2019 to 2022 shows that while incomes technically increased in core Camden during the post-COVID period, the gap relative to 08106 stayed the same or got wider. The recovery was not equal.

---

## How to Run It

1. Get a free Census API key at https://api.census.gov/data/key_signup.html
2. Add your key to collect_data.py
3. Run collect_data.py to pull the data and generate camden_data.csv
4. Fill in your Snowflake credentials in load_to_snowflake.py
5. Create a database called CAMDEN_ANALYSIS in Snowflake
6. Run load_to_snowflake.py to build the tables and load the data
7. Run the queries in analysis_queries.sql in your Snowflake worksheet
