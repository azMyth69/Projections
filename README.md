# Sales Prediction Tool

A **Tkinter-based** Python application that predicts next week’s daily **AM** and **PM** sales based on CSV data from the past four weeks. The user can optionally apply **percentage buffers** or **dollar offsets** (catering) to each day of the week before viewing the final sales predictions.

## Table of Contents

1. [Features](#features)  
2. [Prerequisites & Dependencies](#prerequisites--dependencies)  
3. [Usage Guide](#usage-guide)  
   - [Running from Python](#running-from-python)  
   - [Selecting Files & Viewing Predictions](#selecting-files--viewing-predictions)  
   - [Configuring Buffers (Percentage)](#configuring-buffers-percentage)  
   - [Configuring Catering (Dollar Offsets)](#configuring-catering-dollar-offsets)  
4. [CSV Format Requirements](#csv-format-requirements)  
5. [How It Works](#how-it-works)  
6. [License](#license)

---

## Features

- **AM/PM CSV File Selection**  
  - Select two separate CSV files: one for morning (AM) sales data and one for evening (PM) sales data.

- **Automated Date Filtering**  
  - Takes the most recent date in your dataset and automatically looks back **4 weeks (28 days)** for average daily sales.

- **Day Sorting**  
  - Displays predictions from **Wednesday to Tuesday**, rather than the standard Monday–Sunday.

- **Prediction View & Saving**  
  - Shows final predictions in a popup.  
  - Also writes them to a **`sales_predictions.txt`** file.

- **Buffer Configuration (Percentage)**  
  - Optionally increase/decrease daily sales by a percentage (e.g., +10% on Wednesdays, -5% on Mondays).

- **Catering Configuration (Dollar Offsets)**  
  - Optionally add or subtract a fixed dollar amount per day (e.g., +\$5 on Monday).

- **Dark Gray UI Theme**  
  - Provides a consistent dark-themed look for the main window and all sub-windows.

- **Tooltips**  
  - Hover over **“?”** next to the **Buffers** or **Catering** buttons to see a brief description of each feature.

---

## Prerequisites & Dependencies

1. **Python 3.7+**  
2. **Pandas** library for data manipulation:  
   \[
     \texttt{pip install pandas}
   \]  
3. **Tkinter**  
   - Usually included with standard Python on Windows/macOS.  
   - For some Linux distros, you may need to install `python3-tk`.

---

## Usage Guide

### Running from Python

1. **Clone or Download** the project folder.  
2. Open a **Terminal** or **Command Prompt** in that folder.  
3. Run:
   ```bash
   python "Projections-gui 2.0.py"
   ```
4.The “Sales Prediction” window will appear.

### Selecting Files & Viewing Predictions

1. Click “Select AM Sales CSV File” and choose your morning sales CSV file (e.g. AM_data.csv).
2. Click “Select PM Sales CSV File” and choose your evening sales CSV file (e.g. PM_data.csv).
3. Click “Submit” to generate next week’s predictions.

### Configuring Buffers (Percentage)

1. Click “Configure Buffers”.
2. For each day of the week, type a percentage (e.g., 10 for +10%, -5 for -5%).
3. Click “Save” to store your changes.
4. The next time you click “Submit”, the predictions for each day will be multiplied by (1 + percentage).

### Configuring Catering (Dollar Offset)

1. Click “Catering”.
2. For each day, type a dollar amount (e.g., 5 for +$5, -3 for -$3).
3. Click “Save” to store your changes.
4. The next time you click “Submit”, that amount is added to each day’s predicted sales after applying any percentage buffer.

## CSV Format Requriements

- The script reads two columns from your CSV:

# TextBox4: Contains dates in the format "Day of Week, Month DD, YYYY" (e.g., "Wednesday, August 23, 2023").

# TextBox3: Contains sales amounts with dollar signs/commas optionally included (e.g., "$1,234.56").

### How It Works

1. Loading Data

- Reads the CSV columns: TextBox4 (dates) and TextBox3 (sales).
- Converts dates to a datetime and filters to the last 28 days.

2. Aggregating Sales

- Groups by day of the week and calculates the average sales for each day (Wed–Tue).

3. Predicting Next Week

- Finds the latest date in the dataset.
- Calculates the next Wednesday and assigns daily predictions (Wed–Tue).

4. Applying Buffers & Offsets

- Buffers (day_to_buffer) multiply the daily average by (1 + buffer).
- Catering (day_to_offset) adds or subtracts a dollar amount.
- Final formula: new_value = (old_value×(1+buffer))+offset

5. Displaying & Saving
- Shows predictions in a popup window.
- Saves them to ```sales_predictions.txt```

### License

This project is released with no specific license by default. Feel free to modify, distribute, or use it as needed. If your use case requires a particular license, please add or update this section.
