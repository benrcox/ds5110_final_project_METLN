# Andrew Fumarola
# DS 5110 Final Project - METFLN
# LogAnalysis

from LogAnalysis import daily_counts
import pandas as pd
import matplotlib.pyplot as plt

def rate_zip(z, log, can, new):
    """
    Finds churn rate and retention rate given a zip code
    params:
        z: the zip code in string format
        log: the full subscriber log
        can: the cancelled accounts log
        new: the new accounts log
        (log, can, new are created in LogCompiler and LogAnalysis scripts)
    return:
        churn_rate, reten_rate
    """
    z_log = log[log["Zip"] == z]
    z_can = can[can["Zip"] == z]
    z_new = new[new["Zip"] == z]

    latest_date = z_log['LogDate'].max()
    earliest_date = z_log['LogDate'].min()
    full_date_range = pd.date_range(earliest_date, latest_date)

    c_log = daily_counts(z_log, "LogDate", full_date_range)
    c_can = daily_counts(z_can, "LogDate", full_date_range)
    start_n = c_log.iloc[0] 
    loss = c_can.sum()
    churn_rate = round((loss / start_n) * 100, 2)

    first_day_group = z_log[z_log["LogDate"] == earliest_date]
    last_day_group = z_log[z_log["LogDate"] == latest_date]
    common_count = last_day_group["AccoutID"].isin(first_day_group["AccoutID"]).sum()

    reten_rate = round((common_count / start_n) * 100, 2)
    return(churn_rate, reten_rate)

def main():
    # Clean data types for processing
    log = pd.read_csv("SubscriberLog.csv", sep=',')
    can = pd.read_csv("CancelledAccounts.csv", sep=",")
    new = pd.read_csv("NewAccounts.csv", sep=",")

    log['AccoutID'] = log['AccoutID'].astype('string')
    can['AccoutID'] = can['AccoutID'].astype('string')
    new['AccoutID'] = new['AccoutID'].astype('string')

    for df in [log, can, new]:
        df['Zip'] = df['Zip'].astype(str).str.zfill(5)
        df['LogDate'] = pd.to_datetime(df['LogDate'])

    # Isolate zip codes of interest (with appearances over x times in log and in Maine)
    x = 500
    zip_counts = log["Zip"].value_counts()
    zips_over_x = zip_counts[zip_counts > x].index.tolist()

    all_zips = pd.read_csv("zip_code_database.csv", sep=",")
    all_zips['zip'] = all_zips['zip'].astype(str).str.zfill(5)
    maine_zips = all_zips[all_zips['statzTe'] == "ME"]
    zips_over_x_in_maine = maine_zips[maine_zips['zip'].isin(zips_over_x)]['zip'].tolist()
    
    # Run rate_zip for each zip code in Maine, create CSV
    # Join with city names from zip code database, sort
    rows = []
    for z in zips_over_x_in_maine:
        churn, retention = rate_zip(z, log, can, new)
        rows.append({"zip": z, "ChurnRate": churn, "RetentionRate": retention})

    zip_cities = all_zips[["zip", "primary_city"]]
    rates_by_zip = pd.DataFrame(rows)
    full_rates = pd.merge(rates_by_zip, zip_cities, on="zip", how="inner")
    full_rates.sort_values(by="ChurnRate", inplace=True, ascending=False)
    full_rates.to_csv("RatesByZip.csv", sep=",")
    
if __name__ == "__main__":
    main()