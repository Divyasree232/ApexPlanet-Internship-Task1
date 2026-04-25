import pandas as pd
import numpy as np
from datetime import datetime
import os

print("=" * 60)
print("DATA CLEANING REPORT - CAFE SALES DATASET")
print("=" * 60)

# Load the dataset
df = pd.read_csv('dirty_cafe_sales.csv')

# 1. INITIAL DATA OVERVIEW

print("\n1. INITIAL DATA OVERVIEW")
print("-" * 40)
print(f"Original shape: {df.shape}")
print(f"Original columns: {list(df.columns)}")


# 2. HANDLE MISSING VALUES

print("\n2. HANDLING MISSING VALUES")
print("-" * 40)

# Replace empty strings with NaN
df = df.replace(r'^\s*$', np.nan, regex=True)

# Check missing values before cleaning
missing_before = df.isnull().sum()
print("Missing values before cleaning:")
for col, count in missing_before.items():
    if count > 0:
        print(f"  {col}: {count} ({count/len(df)*100:.2f}%)")

# Clean Item column
df['Item'] = df['Item'].fillna('Unknown')
df['Item'] = df['Item'].replace('UNKNOWN', 'Unknown')
df['Item'] = df['Item'].replace('ERROR', 'Unknown')

# Clean Quantity
df['Quantity_cleaned'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['Quantity_cleaned'] = df['Quantity_cleaned'].fillna(1)
df['Quantity_cleaned'] = df['Quantity_cleaned'].clip(lower=1, upper=50)

# Clean Price Per Unit
df['Price_cleaned'] = pd.to_numeric(df['Price Per Unit'], errors='coerce')

# Fill missing prices based on item averages
item_price_map = df.groupby('Item')['Price_cleaned'].mean().to_dict()
default_prices = {
    'Coffee': 2.0, 'Cake': 3.0, 'Cookie': 1.0, 'Salad': 5.0,
    'Sandwich': 4.0, 'Smoothie': 4.0, 'Juice': 3.0, 'Tea': 1.5,
    'Unknown': 3.0
}

for item in default_prices:
    if item not in item_price_map or pd.isna(item_price_map[item]):
        item_price_map[item] = default_prices[item]

df['Price_cleaned'] = df.apply(
    lambda row: item_price_map.get(row['Item'], 3.0) if pd.isna(row['Price_cleaned']) else row['Price_cleaned'],
    axis=1
)
df['Price_cleaned'] = df['Price_cleaned'].clip(lower=0.5, upper=50)

# Clean Total Spent
df['Total_cleaned'] = pd.to_numeric(df['Total Spent'], errors='coerce')
mask_recalculate = (df['Total_cleaned'].isna()) | (abs(df['Total_cleaned'] - df['Quantity_cleaned'] * df['Price_cleaned']) > 0.01)
df['Total_cleaned'] = df.apply(
    lambda row: row['Quantity_cleaned'] * row['Price_cleaned'] if mask_recalculate[row.name] else row['Total_cleaned'],
    axis=1
)

# Clean Payment Method
df['Payment_cleaned'] = df['Payment Method'].fillna('Unknown')
df['Payment_cleaned'] = df['Payment_cleaned'].replace('ERROR', 'Unknown')
df['Payment_cleaned'] = df['Payment_cleaned'].replace('UNKNOWN', 'Unknown')
df['Payment_cleaned'] = df['Payment_cleaned'].str.title()

# Clean Location
df['Location_cleaned'] = df['Location'].fillna('Unknown')
df['Location_cleaned'] = df['Location_cleaned'].replace('ERROR', 'Unknown')
df['Location_cleaned'] = df['Location_cleaned'].replace('UNKNOWN', 'Unknown')
df['Location_cleaned'] = df['Location_cleaned'].str.title()

# Clean Transaction Date
def clean_date(date_str):
    if pd.isna(date_str):
        return np.nan
    if date_str == 'ERROR':
        return np.nan
    try:
        return pd.to_datetime(date_str, format='%Y-%m-%d')
    except:
        return np.nan

df['Date_cleaned'] = df['Transaction Date'].apply(clean_date)


# 3. REMOVE DUPLICATES

print("\n3. REMOVING DUPLICATES")
print("-" * 40)
duplicates_before = df.duplicated(subset=['Transaction ID']).sum()
print(f"Duplicate Transaction IDs: {duplicates_before}")
df = df.drop_duplicates(subset=['Transaction ID'], keep='first')


# 4. FEATURE ENGINEERING

print("\n4. FEATURE ENGINEERING")
print("-" * 40)

# Create derived columns
df['Day_of_Week'] = df['Date_cleaned'].dt.day_name()
df['Month'] = df['Date_cleaned'].dt.month_name()
df['Year'] = df['Date_cleaned'].dt.year
df['Quarter'] = df['Date_cleaned'].dt.quarter
df['Is_Weekend'] = df['Day_of_Week'].isin(['Saturday', 'Sunday'])

# Price category
def price_category(price):
    if price < 2:
        return 'Low'
    elif price < 4:
        return 'Medium'
    else:
        return 'High'

df['Price_Category'] = df['Price_cleaned'].apply(price_category)

# Transaction value category
def value_category(total):
    if total < 5:
        return 'Small'
    elif total < 15:
        return 'Medium'
    else:
        return 'Large'

df['Value_Category'] = df['Total_cleaned'].apply(value_category)

# Item category
item_categories = {
    'Beverage': ['Coffee', 'Tea', 'Juice', 'Smoothie'],
    'Food': ['Cake', 'Cookie', 'Salad', 'Sandwich']
}
df['Item_Category'] = df['Item'].apply(
    lambda x: next((cat for cat, items in item_categories.items() if x in items), 'Other')
)


# 5. HANDLE OUTLIERS

print("\n5. HANDLING OUTLIERS")
print("-" * 40)

Q1 = df['Total_cleaned'].quantile(0.25)
Q3 = df['Total_cleaned'].quantile(0.75)
IQR = Q3 - Q1
outlier_threshold_upper = Q3 + 1.5 * IQR

outliers = df[df['Total_cleaned'] > outlier_threshold_upper]
print(f"Outliers in Total Spent (> {outlier_threshold_upper:.2f}): {len(outliers)} rows")

cap_value = df['Total_cleaned'].quantile(0.99)
df['Total_cleaned'] = df['Total_cleaned'].clip(upper=cap_value)
print(f"Total Spent capped at 99th percentile: {cap_value:.2f}")


# 6. CREATE FINAL DATASET

print("\n6. CREATING FINAL DATASET")
print("-" * 40)

final_df = pd.DataFrame({
    'transaction_id': df['Transaction ID'],
    'item': df['Item'].str.title(),
    'quantity': df['Quantity_cleaned'],
    'price_per_unit': df['Price_cleaned'],
    'total_spent': df['Total_cleaned'],
    'payment_method': df['Payment_cleaned'],
    'location': df['Location_cleaned'],
    'transaction_date': df['Date_cleaned'],
    'day_of_week': df['Day_of_Week'],
    'month': df['Month'],
    'year': df['Year'],
    'quarter': df['Quarter'],
    'is_weekend': df['Is_Weekend'],
    'price_category': df['Price_Category'],
    'value_category': df['Value_Category'],
    'item_category': df['Item_Category']
})

rows_without_date = final_df['transaction_date'].isna().sum()
print(f"Rows without valid transaction date: {rows_without_date}")

final_df = final_df.sort_values('transaction_date', na_position='last')

print(f"\nFinal dataset shape: {final_df.shape}")


# 7. DATA QUALITY METRICS

print("\n7. DATA QUALITY METRICS")
print("-" * 40)

print("\nMissing values after cleaning:")
for col in final_df.columns:
    missing = final_df[col].isna().sum()
    if missing > 0:
        print(f"  {col}: {missing} ({missing/len(final_df)*100:.2f}%)")

print("\nData types after cleaning:")
for col in final_df.columns:
    print(f"  {col}: {final_df[col].dtype}")

print("\nSample of cleaned data (first 10 rows):")
print(final_df.head(10))


# 8. EXPORT CLEANED DATASET (WITH ERROR HANDLING)

print("\n8. EXPORTING CLEANED DATASET")
print("-" * 40)

# Check if file is open and handle gracefully
output_file = 'cafe_sales_cleaned.csv'
try:
    final_df.to_csv(output_file, index=False)
    print(f"Cleaned dataset saved to: {output_file}")
except PermissionError:
    print(f"ERROR: Cannot save to '{output_file}' - file may be open in another program.")
    print("Please close any programs that might have this file open (Excel, Notepad, etc.)")
    
    # Try alternative filename
    alt_file = 'cafe_sales_cleaned_new.csv'
    final_df.to_csv(alt_file, index=False)
    print(f"Saved as alternative: {alt_file}")

# Save summary statistics
summary_file = 'cafe_sales_summary.csv'
try:
    summary_stats = final_df.describe()
    summary_stats.to_csv(summary_file)
    print(f"Summary statistics saved to: {summary_file}")
except PermissionError:
    alt_summary = 'cafe_sales_summary_new.csv'
    summary_stats.to_csv(alt_summary)
    print(f"Summary saved as: {alt_summary}")

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 60)

# Display key insights
print("\nKEY INSIGHTS FROM CLEANED DATA:")
print("-" * 40)
print(f"Total valid transactions: {len(final_df)}")
if final_df['transaction_date'].notna().any():
    print(f"Date range: {final_df['transaction_date'].min()} to {final_df['transaction_date'].max()}")
print(f"Unique items: {final_df['item'].nunique()}")
print(f"Total revenue: ${final_df['total_spent'].sum():,.2f}")
print(f"Average transaction value: ${final_df['total_spent'].mean():.2f}")