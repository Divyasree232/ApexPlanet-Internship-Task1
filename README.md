# DA TASK 1: Data Cleaning & Wrangling

## APEX PLANET Internship - Data Analytics Track

---

## Project Overview

This project demonstrates essential data cleaning and preparation techniques on a messy cafe sales dataset. The raw data contained significant quality issues that needed to be addressed before any meaningful analysis could be performed.

### Dataset Details
- **Source**: Cafe sales transactions
- **Size**: 10,000 rows × 8 columns
- **Time Period**: January 2023 - December 2023

---

##  Data Quality Issues Identified (BEFORE CLEANING)

| Issue Type | Examples | Severity |
|------------|----------|----------|
| Missing Values | Empty cells in 7 columns | High |
| Invalid Values | "ERROR", "UNKNOWN" in data fields | High |
| Wrong Data Types | Numbers stored as text strings | High |
| Calculation Errors | Total Spent ≠ Quantity × Price | Medium |
| Inconsistent Formatting | Mixed categorical values | Medium |
| Outliers | Extremely high/low transaction values | Low |

### Missing Values Breakdown (Before)
- Payment Method: 25.79% missing
- Location: 32.65% missing
- Item: 3.33% missing
- Transaction Date: 1.59% missing
- Other columns: <2% missing

---

##  Cleaning Operations Performed

### 1. Data Type Conversion
| Column | Before | After |
|--------|--------|-------|
| Quantity | `str` (had "ERROR") | `float64` |
| Price Per Unit | `str` (had "ERROR") | `float64` |
| Total Spent | `str` | `float64` |
| Transaction Date | `str` | `datetime64` |

### 2. Missing Value Treatment
- Filled missing items with 'Unknown'
- Imputed missing prices using item averages
- Default quantity to 1 when missing
- Recalculated missing total spent values
- Standardized 'Unknown' for missing categorical data

### 3. Error Handling
- Replaced "ERROR" strings with appropriate values
- Recalculated total spent where original was incorrect

### 4. Outlier Treatment
- Identified outliers using IQR method (Q3 + 1.5×IQR)
- Capped values at 99th percentile

### 5. Feature Engineering (8 new columns)
| New Column | Description |
|------------|-------------|
| day_of_week | Monday - Sunday |
| month | January - December |
| year | 2023 |
| quarter | 1, 2, 3, 4 |
| is_weekend | True/False flag |
| price_category | Low (<$2), Medium ($2-4), High (>$4) |
| value_category | Small (<$5), Medium ($5-15), Large (>$15) |
| item_category | Beverage, Food, Other |

---

##  Results & Insights (AFTER CLEANING)

### Data Quality Metrics

Total transactions: 10,000
Total revenue: $86,566.83
Average transaction: $8.66
Unique items: 9 (including 'Unknown' as a category)
Date range: 2023-01-01 to 2023-12-31
Zero "ERROR" strings remaining
All numeric columns now have proper data types


### What Was Fixed vs What Remains

| Fixed Issues | Before | After |
|-------------|--------|-------|
| "ERROR" in Quantity | `"ERROR"` | `1.0` (float) |
| "ERROR" in Price | `"ERROR"` | Default price based on item |
| Total Spent mismatch | Wrong calculation | Recalculated from Qty × Price |
| Date with "ERROR" | `"ERROR"` | `NaN` (null value) |
| All columns as strings | `object` dtype | Proper types (`float64`, `datetime64`) |

| Intentional Placeholders | Why Kept |
|--------------------------|----------|
| `"Unknown"` in Item | Missing product info - deleting would lose 3% of data |
| `"Unknown"` in Payment Method | Missing payment data - deleting would lose 26% of data |
| `"Unknown"` in Location | Missing location data - deleting would lose 33% of data |

> **Note**: "Unknown" values are NOT errors. They represent missing data that was standardized during cleaning. Analysts can choose to filter them out or keep them as a separate category based on analysis needs.


