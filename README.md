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
