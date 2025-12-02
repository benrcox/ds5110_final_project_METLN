# Andrew Fumarola
# DS 5110 Final Project - METFLN
# LogAnalysis

# This script analyzes a master log as created in LogCompiler.py
# Creates labels for first and last instances of account IDs in log
# Plots for DAUs over time and account creations/cancellations over time

import pandas as pd
import matplotlib.pyplot as plt

def daily_counts(df, date_col, daterange):
        """
        param:  df: the summary data frame
                date_col: the column name with date where count is taking place
        returns a dataframe with the count of subscriber type on each day
        """
        counts = df.groupby(date_col).size()
        counts = counts.reindex(daterange, fill_value=0)
        return counts

def last_active_day_label(l):
        """
        Iterates through log and labels entries where it is the last seen appearance of that account ID
        Param: l: the subscriber log
        Returns: l: the subscriber log
        """
        l = l.sort_values(['AccoutID','LogDate'])
        l['next_log'] = l.groupby('AccoutID')['LogDate'].shift(-1)
        l['last_active_day'] = l['next_log'].isna()
        return(l)

def first_active_day_label(l):
    """
    Iterates through log and labels entries where it is the first seen appearance of that account ID
    Param: l: the subscriber log
    Returns: l: the subscriber log
    """
    l = l.sort_values(['AccoutID','LogDate'])
    l['first_active_day'] = l.groupby('AccoutID').cumcount() == 0
    return(l)

def main():

    log = pd.read_csv("SubscriberLog.csv", sep=',')
    
    # Using above functions to label first and last active days
    log = last_active_day_label(log)
    log = first_active_day_label(log)

    # Find date range for later processing
    latest_date = log['LogDate'].max()
    earliest_date = log['LogDate'].min()
    full_date_range = pd.date_range(log['LogDate'].min(), log['LogDate'].max())

    # Create df of accounts that cancel in the log range
    # Only adds the log entry of that last day
    # Ensures that the log date is not the latest date in log
    cancelled_accounts = log[(log['LogDate'] != latest_date) & (log['last_active_day'] == True)]
    cancelled_accounts.to_csv("CancelledAccounts.csv", sep=',', index=False)

    # Create df of accounts that are new in the log range
    # Only adds the log entry of that first day
    # Ensures that the log date is not the earliest date in log
    new_accounts = log[(log['LogDate'] != earliest_date) & (log['first_active_day'] == True)]
    new_accounts.to_csv("NewAccounts.csv", sep=',', index=False)

    log.loc[:, 'LogDate'] = pd.to_datetime(log['LogDate'])
    new_accounts.loc[:, 'LogDate'] = pd.to_datetime(new_accounts['LogDate'])
    cancelled_accounts.loc[:, 'LogDate'] = pd.to_datetime(cancelled_accounts['LogDate'])

    # Daily counts
    # Use the daily_counts function to create dfs that have count by day
    # Daily Active Users
    full_counts = daily_counts(log, 'LogDate', full_date_range)
    # Daily New Accounts
    new_counts = daily_counts(new_accounts, 'LogDate', full_date_range)
    # Daily Cancellations
    cancel_counts = daily_counts(cancelled_accounts, 'LogDate', full_date_range)

    # Plot full daily active users over time
    plt.plot(full_counts.index, full_counts.values, marker='o', label="Total Subscribers")
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.title('Daily Active User Totals')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    plt.close()

    # Plot new accounts and cancelled accounts over time
    plt.figure(figsize=(12,6))
    plt.plot(cancel_counts.index, cancel_counts.values, marker='o', label="Cancellations")
    plt.plot(new_counts.index, new_counts.values, marker='x', label="New Accounts")
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.title('Daily User Changes')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()