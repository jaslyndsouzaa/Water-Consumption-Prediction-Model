import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\jasly\OneDrive\Documents\College\6TH SEMESTER\Project\WCPM\waterconsumptionprediction-firebase-adminsdk-uq110-7bc5a33f9a.json")
firebase_admin.initialize_app(cred, {
    "databaseURL":"https://waterconsumptionprediction-default-rtdb.firebaseio.com"
})

# Read data from Firebase
ref = db.reference('WaterBillData')
data = ref.get()

# Convert data to a pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')

# Preprocess data
df['BillDate'] = pd.to_datetime(df['BillDate'], errors='coerce', format='%Y-%m-%d')
df['Month'] = df['BillDate'].dt.month.astype('Int64')
df['Year'] = df['BillDate'].dt.year.astype('Int64')

ohe = OneHotEncoder()
transformed = ohe.fit_transform(df[['BlockName']])
df[ohe.categories_[0]] = transformed.toarray()

df['UnitsConsumed'] = df['UnitsConsumed'].astype('int')
df['TotalBill'] = df['TotalBill'].str.replace(',', '').str.replace('$', '').astype(float)
df['TotalBill'] = df['TotalBill'].astype(int)

df = df.drop(columns=['BlockName', 'BillDate'])
df = df.reset_index(drop=True).set_index('TotalBill')

scaler = MinMaxScaler(feature_range=(0, 1))
x_train, x_test, y_train, y_test = train_test_split(df.drop(['UnitsConsumed'], axis=1), df['UnitsConsumed'],
                                                     test_size=0.2, random_state=1, shuffle=True)
scaler.fit(x_train)
x_train_scaled = pd.DataFrame(scaler.transform(x_train), columns=x_train.columns)
x_test_scaled = pd.DataFrame(scaler.transform(x_test), columns=x_test.columns)

# Train model
rf = RandomForestRegressor(n_estimators=400, max_features='sqrt', max_depth=7, random_state=2)
rf.fit(x_train_scaled, y_train)

# Save model as pickle file
with open('MainModel.pkl', 'wb') as file:
    pickle.dump(rf, file)

with open('MainScaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

# Save encoder object as pickle file
with open('MainEncoder.pkl', 'wb') as file:
    pickle.dump(ohe, file)
