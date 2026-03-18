import requests
import pandas as pd

API_KEY = "c1006779a680d98e229637053d42913a0d7f8ddb"

ZIP_CODES = ["08102", "08103", "08104", "08105", "08106"]
YEARS = [2019, 2021, 2022]

# subject table variables
# pulling income, poverty, unemployment, education, insurance, snap all at once
SUBJECT_VARS = ",".join([
    "S1901_C01_012E",   # median household income
    "S1701_C03_001E",   # poverty rate
    "S2301_C04_001E",   # unemployment rate
    "S1501_C02_015E",   # pct high school grad or higher (25+)
    "S2701_C05_001E",   # pct uninsured
    "S2201_C03_001E",   # pct households receiving SNAP
])

# profile table variables -- rent, vehicle access, race breakdown
PROFILE_VARS = ",".join([
    "DP04_0134E",       # median gross rent
    "DP04_0058PE",      # pct occupied units with no vehicle
    "DP05_0071PE",      # pct hispanic or latino
    "DP05_0077PE",      # pct white alone
    "DP05_0078PE",      # pct black or african american
])


def fetch_subject(year, zip_code):
    url = f"https://api.census.gov/data/{year}/acs/acs5/subject"
    params = {
        "get": SUBJECT_VARS,
        "for": f"zip code tabulation area:{zip_code}",
        "key": API_KEY
    }
    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"  subject table failed for {zip_code} {year}: {resp.status_code}")
            return {}
        data = resp.json()
        if len(data) < 2:
            return {}
        return dict(zip(data[0], data[1]))
    except Exception as e:
        print(f"  error fetching subject for {zip_code} {year}: {e}")
        return {}


def fetch_profile(year, zip_code):
    url = f"https://api.census.gov/data/{year}/acs/acs5/profile"
    params = {
        "get": PROFILE_VARS,
        "for": f"zip code tabulation area:{zip_code}",
        "key": API_KEY
    }
    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"  profile table failed for {zip_code} {year}: {resp.status_code}")
            return {}
        data = resp.json()
        if len(data) < 2:
            return {}
        return dict(zip(data[0], data[1]))
    except Exception as e:
        print(f"  error fetching profile for {zip_code} {year}: {e}")
        return {}


results = []

for year in YEARS:
    print(f"pulling {year}...")
    for zip_code in ZIP_CODES:
        row = {"zip_code": zip_code, "year": year}

        subject = fetch_subject(year, zip_code)
        profile = fetch_profile(year, zip_code)

        row["median_income"]     = subject.get("S1901_C01_012E")
        row["poverty_rate"]      = subject.get("S1701_C03_001E")
        row["unemployment_rate"] = subject.get("S2301_C04_001E")
        row["hs_grad_rate"]      = subject.get("S1501_C02_015E")
        row["uninsured_rate"]    = subject.get("S2701_C05_001E")
        row["snap_rate"]         = subject.get("S2201_C03_001E")
        row["median_gross_rent"] = profile.get("DP04_0134E")
        row["no_vehicle_pct"]    = profile.get("DP04_0058PE")
        row["pct_hispanic"]      = profile.get("DP05_0071PE")
        row["pct_white"]         = profile.get("DP05_0077PE")
        row["pct_black"]         = profile.get("DP05_0078PE")

        results.append(row)

df = pd.DataFrame(results)

# census uses -666666666 for missing, replace with NaN
numeric_cols = [
    "median_income", "poverty_rate", "unemployment_rate", "hs_grad_rate",
    "uninsured_rate", "snap_rate", "median_gross_rent", "no_vehicle_pct",
    "pct_hispanic", "pct_white", "pct_black"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].where(df[col] >= 0, other=None)

print("\n", df.to_string(index=False))
df.to_csv("camden_data.csv", index=False)
print(f"\nsaved {len(df)} rows to camden_data.csv")
