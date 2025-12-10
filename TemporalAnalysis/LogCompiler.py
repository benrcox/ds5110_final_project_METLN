# Andrew Fumarola
# DS 5110 Final Project - METFLN
# LogCompiler

# This script contains methods to compile a full log from a folder of SubscriberList daily logs
# IMPORTANT to edit the file_source_path variable below: give the file path to folder containing SubscriberLists
# File source should include all txt files llke "SubscriberListRMMDDYY.txt"

import pandas as pd
import os

def get_file_names(path):
    """
    param: path: the path to folder
    collects list of file names in given folder
    only returns those that end with "txt"
    """
    l = []
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path) and full_path[-3:]=="txt":
            l.append(item)
    return l

def date_clean(s):
    """
    Returns a datetime object from a MMDDYY formatted string
    """
    return pd.to_datetime(s, format="%m-%d-%y")

def compile_full_log(source_path):
    """
    param: source_path: the path to a folder with files like "SubscriberListRMMDDYY.txt"
    creates and saves a dataframe with all data from all subscriber list logs
    return: none - saves "SubscriberLog.csv" to relative folder
    """

    file_list = get_file_names(source_path)
    full_df = pd.DataFrame()

    for f in file_list:
        d = pd.read_csv(f, sep='|')
        d["City"] = d["City"].astype(str).str.lower()
        d["State"] = d["State"].astype(str).str.upper()
        d["LastStartDate"] = date_clean(d["LastStartDate"])
        d["OriginalStartDate"] = date_clean(d["OriginalStartDate"])
        day = f[17:19]
        month = f[15:17]
        year = f[19:21]
        raw_log_date = f"{month}-{day}-{year}" # Adding the date from file name
        d["LogDate"] = date_clean(raw_log_date)
        d["ActiveDays"] = (d["LogDate"] - d["LastStartDate"]).dt.days
        full_df = pd.concat([d, full_df], ignore_index=True)

    full_df.to_csv("SubscriberLog.csv", sep=',', index=False)

def main():
    file_source_path = "/Users/andrewfumarola/Documents/School/DS5110 Essentials of Data Science/FinalProject"
    # Input file source path here, return full log
    compile_full_log(file_source_path)

if __name__ == "__main__":
    main()