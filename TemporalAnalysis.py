# Andrew Fumarola
# DS 5110 Final Project - METFLN
# AcctChangeAnalysis

import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

log = pd.read_csv("SubscriberLog.csv", sep=',')
can = pd.read_csv("CancelledAccounts.csv", sep=",")
new = pd.read_csv("NewAccounts.csv", sep=",")

user_dems = log[["Publication", "AccoutID", "Status",
                 "Bill Method", "Dist ID",
                 "Route ID", "Day pattern",
                 "City", "State", "Zip", "Rate Code"]].drop_duplicates().copy()

user_dems["Cancellation"] = user_dems["AccoutID"].isin(can["AccoutID"])
user_dems["New"] = user_dems["AccoutID"].isin(new["AccoutID"])

def account_change_viewer(variable, type):
    """
    Views head of aggregated count of new accounts or cancelled accounts by variable
    param:  variable: the targeted variable to group by, e.g. "Zip"
            type: cancellations or new accounts, must be "Cancellation" or "New"
    print:  head of groupby df
    """
    c = user_dems.groupby(variable)[type].sum().sort_values(ascending=False)
    print("Viewing " + type + " Accounts by " + variable)
    print(c.head())

account_change_viewer("Zip", "Cancellation")

# Cancellation Predictive Algorithm
"""
x = user_dems[["Publication", "Status","Bill Method", "Day pattern", "Zip"]]
x = pd.get_dummies(x, drop_first=True)

y = user_dems["Cancellation"]

X_train, X_test, y_train, y_test = train_test_split(x,y, test_size = 0.2)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

clf3 = tree.DecisionTreeClassifier()

# DT train and test
clf3.fit(X_train_scaled,y_train)
pre3 = clf3.predict(X_test_scaled)

print("\n----DecTree----")
print(str(100*(round((y_test==pre3).sum()/len(pre3), 4))) + "%")
print(confusion_matrix(y_test, pre3))
"""