import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import matplotlib.pyplot as plt
import joblib

# Load data
original_df = pd.read_excel('NaturalGasDemand_Input.xlsx', engine='openpyxl')
original_df['Month'] = pd.to_datetime(original_df['Month'])
original_df.set_index('Month', inplace=True)

# Add time features
original_df['Year'] = original_df.index.year
original_df['Month_num'] = original_df.index.month
original_df['Quarter'] = original_df.index.quarter
# Optionally, add cyclical encoding for month
original_df['Month_sin'] = np.sin(2 * np.pi * original_df['Month_num'] / 12)
original_df['Month_cos'] = np.cos(2 * np.pi * original_df['Month_num'] / 12)

target_col = 'India total Consumption of Natural Gas (in BCM)'
X = original_df.drop(columns=[target_col])
y = original_df[target_col]

# Train-test split (no shuffle)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Standardization
scaler = StandardScaler()
scaler.fit(X_train)
joblib.dump(scaler, 'scaler.save')
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest (basic)
rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
rf_model.fit(X_train_scaled, y_train)
joblib.dump(rf_model, 'natural_gas_rf_model.pkl')
rf_pred = rf_model.predict(X_test_scaled)
rf_results = pd.DataFrame({'Month': y_test.index, 'Actual': y_test.values, 'Predicted': rf_pred})
rf_results.to_excel('rf_test_vs_prediction_results.xlsx', index=False)
plt.figure(figsize=(10,6))
plt.plot(y_test.index, y_test, label='Actual')
plt.plot(y_test.index, rf_pred, label='RF Predicted')
plt.legend()
plt.title('Random Forest: Test vs Prediction (No Feature Engineering)')
plt.xlabel('Month')
plt.ylabel(target_col)
plt.tight_layout()
plt.savefig('rf_test_vs_prediction.png')
plt.close()

# Train XGBoost (basic)
xgb_model = xgb.XGBRegressor(n_estimators=200, random_state=42)
xgb_model.fit(X_train_scaled, y_train)
joblib.dump(xgb_model, 'natural_gas_xgb_model.pkl')
xgb_pred = xgb_model.predict(X_test_scaled)
xgb_results = pd.DataFrame({'Month': y_test.index, 'Actual': y_test.values, 'Predicted': xgb_pred})
xgb_results.to_excel('xgb_test_vs_prediction_results.xlsx', index=False)
plt.figure(figsize=(10,6))
plt.plot(y_test.index, y_test, label='Actual')
plt.plot(y_test.index, xgb_pred, label='XGB Predicted')
plt.legend()
plt.title('XGBoost: Test vs Prediction (No Feature Engineering)')
plt.xlabel('Month')
plt.ylabel(target_col)
plt.tight_layout()
plt.savefig('xgb_test_vs_prediction.png')
plt.close()

# Save feature names for Flask app
with open('feature_names.txt', 'w') as f:
    for col in X_train.columns:
        f.write(f"{col}\n")

print('Baseline models (RF, XGB) trained and results saved.')
