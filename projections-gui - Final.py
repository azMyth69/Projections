import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# -------------------------------------------------------------------------
# Tooltip Class
# -------------------------------------------------------------------------
class ToolTip:
    """
    Basic tooltip class for Tkinter.
    When the user hovers over the associated widget, a small pop-up appears
    showing the 'text' passed in. When the mouse leaves, the pop-up disappears.
    """

    def __init__(self, widget, text="Tooltip"):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Create a Toplevel window to display the text."""
        if self.tipwindow or not self.text:
            return
        # Position the tooltip slightly offset from the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.configure(bg='yellow', padx=5, pady=5)

        label = tk.Label(tw, text=self.text, justify='left',
                         background='yellow', relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        tw.wm_geometry(f"+{x}+{y}")

    def hide_tip(self, event=None):
        """Destroy the tooltip window."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# -------------------------------------------------------------------------
# Custom Day-of-Week Ordering and Data Logic
# -------------------------------------------------------------------------
DAY_ORDER_DICT = {
    'Wednesday': 0,
    'Thursday': 1,
    'Friday': 2,
    'Saturday': 3,
    'Sunday': 4,
    'Monday': 5,
    'Tuesday': 6
}

def adjust_weekdays(day: str) -> int:
    """Map day names to numeric indices starting from Wednesday."""
    return DAY_ORDER_DICT.get(day, -1)  # Return -1 if the day is not found

def process_file(file_path: str, period: str) -> (pd.DataFrame, pd.Timestamp):
    """Read and process the CSV file for a given period (AM or PM)."""
    df = pd.read_csv(file_path)
    # Keep only necessary columns and rename
    df = df[['TextBox4', 'TextBox3']]
    df.columns = ['date', 'sales_amount']

    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'], format='%A, %B %d, %Y', errors='coerce')
    df = df.dropna(subset=['date'])  # Remove invalid dates

    # Convert 'sales_amount' to float
    df['sales_amount'] = df['sales_amount'].replace('[\$,]', '', regex=True).astype(float)

    # Filter data to the last 4 weeks (28 days)
    end_date = df['date'].max()
    start_date = end_date - pd.Timedelta(days=28)
    df_last_4_weeks = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Add columns for day of the week and day ordering
    df_last_4_weeks['day_of_week'] = df_last_4_weeks['date'].dt.day_name()
    df_last_4_weeks['day_order'] = df_last_4_weeks['day_of_week'].apply(adjust_weekdays)

    # Aggregate (mean) sales by day of the week
    df_daily_sales = (
        df_last_4_weeks.groupby(['day_of_week', 'day_order'])['sales_amount']
        .mean()
        .reset_index()
    )

    # Sort days of week Wednesday -> Tuesday
    df_daily_sales = df_daily_sales.sort_values('day_order')

    # Prepare the predictions
    predicted_sales = df_daily_sales[['day_of_week', 'sales_amount']].copy()
    predicted_sales.columns = ['Day of Week', f'Predicted {period} Sales']
    predicted_sales[f'Predicted {period} Sales'] = (
        predicted_sales[f'Predicted {period} Sales'].round(2)
    )

    return predicted_sales, end_date

def open_file(period: str):
    """Generic file-opening function that sets the correct dictionary values."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        predictions, date_ = process_file(file_path, period)
        predictions_data[period] = predictions
        latest_dates[period] = date_

def open_file_am():
    open_file('AM')

def open_file_pm():
    open_file('PM')

def apply_day_buffers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply percentage-based buffers and dollar offsets to predictions.
    - day_to_buffer[day] = float (0.10 => +10%)
    - day_to_offset[day] = float (5.00 => +$5)

    new_value = (old_value * (1 + buffer_pct)) + offset_val
    """
    for day, buffer_pct in day_to_buffer.items():
        offset_val = day_to_offset.get(day, 0.0)
        mask = df['Day of Week'] == day

        if 'Predicted AM Sales' in df.columns:
            df.loc[mask, 'Predicted AM Sales'] = (
                df.loc[mask, 'Predicted AM Sales'] * (1 + buffer_pct) + offset_val
            )
        if 'Predicted PM Sales' in df.columns:
            df.loc[mask, 'Predicted PM Sales'] = (
                df.loc[mask, 'Predicted PM Sales'] * (1 + buffer_pct) + offset_val
            )

    for col in ['Predicted AM Sales', 'Predicted PM Sales']:
        if col in df.columns:
            df[col] = df[col].round(2)

    return df

def submit_files():
    """Merge AM and PM data, display in a messagebox, and save to file."""
    if predictions_data['AM'] is not None and predictions_data['PM'] is not None:
        combined_predictions = pd.merge(
            predictions_data['AM'],
            predictions_data['PM'],
            on='Day of Week',
            how='outer'
        )

        latest_date = max(latest_dates['AM'], latest_dates['PM'])

        # Next Wednesday (weekday=2)
        days_until_next_wed = (2 - latest_date.weekday() + 7) % 7
        if days_until_next_wed == 0:
            days_until_next_wed = 7
        next_wednesday = latest_date + pd.Timedelta(days=days_until_next_wed)

        # Create date mapping for next 7 days (Wed -> Tue)
        next_week_dates = [
            (next_wednesday + pd.Timedelta(days=i)).strftime('%m/%d')
            for i in range(7)
        ]
        day_order = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
        date_mapping = dict(zip(day_order, next_week_dates))

        combined_predictions['Date'] = combined_predictions['Day of Week'].map(date_mapping)
        combined_predictions['Day with Date'] = (
            combined_predictions['Day of Week'] + " " + combined_predictions['Date']
        )

        combined_predictions['day_order'] = combined_predictions['Day of Week'].apply(adjust_weekdays)
        combined_predictions = combined_predictions.sort_values('day_order')

        # Apply buffers and offsets
        combined_predictions = apply_day_buffers(combined_predictions)

        predictions_text = combined_predictions[
            ['Day with Date', 'Predicted AM Sales', 'Predicted PM Sales']
        ].to_string(index=False)

        messagebox.showinfo("Sales Predictions", predictions_text)

        with open("sales_predictions.txt", "w") as file:
            file.write(predictions_text)

    else:
        messagebox.showwarning("Warning", "Please select both AM and PM sales files.")

# ------------------------------
# Buffer (Percentage) Menu
# ------------------------------
def open_buffer_window():
    buffer_window = tk.Toplevel(root)
    buffer_window.title("Configure Buffers")
    buffer_window.configure(bg=MAIN_BG)

    def save_buffers():
        for day in days_order:
            try:
                val_str = day_entry_vars_pct[day].get().strip()
                if val_str:
                    pct = float(val_str) / 100.0
                    day_to_buffer[day] = pct
                else:
                    day_to_buffer[day] = 0.0
            except ValueError:
                day_to_buffer[day] = 0.0

        buffer_window.destroy()

    day_entry_vars_pct = {}
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Header
    lbl_day_header = tk.Label(
        buffer_window, text="Day", bg=MAIN_BG, fg=LABEL_FG
    )
    lbl_day_header.grid(row=0, column=0, padx=5, pady=5)

    lbl_pct_header = tk.Label(
        buffer_window, text="Percentage (%)", bg=MAIN_BG, fg=LABEL_FG
    )
    lbl_pct_header.grid(row=0, column=1, padx=5, pady=5)

    # Rows for each day
    for i, day in enumerate(days_order, start=1):
        lbl_day = tk.Label(
            buffer_window, text=day, bg=MAIN_BG, fg=LABEL_FG
        )
        lbl_day.grid(row=i, column=0, padx=5, pady=5, sticky='e')

        current_buffer_val = day_to_buffer.get(day, 0.0) * 100
        var_pct = tk.StringVar(value=f"{current_buffer_val:.0f}")
        day_entry_vars_pct[day] = var_pct

        entry_pct = tk.Entry(
            buffer_window, textvariable=var_pct, width=5,
            bg=ENTRY_BG, fg=ENTRY_FG, insertbackground='white'
        )
        entry_pct.grid(row=i, column=1, padx=5, pady=5, sticky='w')

    # Save button
    btn_save = tk.Button(
        buffer_window, text="Save", command=save_buffers,
        bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE_BG, activeforeground=BTN_ACTIVE_FG
    )
    btn_save.grid(row=len(days_order) + 1, column=0, columnspan=2, pady=10)

# ------------------------------
# Catering (Dollar Offsets) Menu
# ------------------------------
def open_catering_window():
    catering_window = tk.Toplevel(root)
    catering_window.title("Catering")
    catering_window.configure(bg=MAIN_BG)

    def save_catering():
        for day in days_order:
            try:
                offset_str = day_entry_vars_offset[day].get().strip()
                if offset_str:
                    offset_val = float(offset_str)
                    day_to_offset[day] = offset_val
                else:
                    day_to_offset[day] = 0.0
            except ValueError:
                day_to_offset[day] = 0.0

        catering_window.destroy()

    day_entry_vars_offset = {}
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Header
    lbl_day_header = tk.Label(
        catering_window, text="Day", bg=MAIN_BG, fg=LABEL_FG
    )
    lbl_day_header.grid(row=0, column=0, padx=5, pady=5)

    lbl_offset_header = tk.Label(
        catering_window, text="Dollar Offset ($)", bg=MAIN_BG, fg=LABEL_FG
    )
    lbl_offset_header.grid(row=0, column=1, padx=5, pady=5)

    # Rows for each day
    for i, day in enumerate(days_order, start=1):
        lbl_day = tk.Label(
            catering_window, text=day, bg=MAIN_BG, fg=LABEL_FG
        )
        lbl_day.grid(row=i, column=0, padx=5, pady=5, sticky='e')

        current_offset_val = day_to_offset.get(day, 0.0)
        var_offset = tk.StringVar(value=f"{current_offset_val:.2f}")
        day_entry_vars_offset[day] = var_offset

        entry_offset = tk.Entry(
            catering_window, textvariable=var_offset, width=7,
            bg=ENTRY_BG, fg=ENTRY_FG, insertbackground='white'
        )
        entry_offset.grid(row=i, column=1, padx=5, pady=5, sticky='w')

    # Save button
    btn_save = tk.Button(
        catering_window, text="Save", command=save_catering,
        bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE_BG, activeforeground=BTN_ACTIVE_FG
    )
    btn_save.grid(row=len(days_order) + 1, column=0, columnspan=2, pady=10)


# -------------------------------------------------------------------------
# Main Application
# -------------------------------------------------------------------------
predictions_data = {'AM': None, 'PM': None}
latest_dates = {'AM': None, 'PM': None}

# Two dictionaries for adjustments:
#   day_to_buffer['Wednesday'] = 0.10 => +10%
#   day_to_offset['Wednesday'] = 5.00 => +$5
day_to_buffer = {}
day_to_offset = {}

root = tk.Tk()
root.title("Sales Prediction")

# ---------- Dark Gray Theme ----------
MAIN_BG = "#2f2f2f"
BTN_BG = "#3f3f3f"
BTN_FG = "white"
BTN_ACTIVE_BG = "#4f4f4f"
BTN_ACTIVE_FG = "white"
LABEL_FG = "white"
ENTRY_BG = "#3f3f3f"
ENTRY_FG = "white"

root.configure(bg=MAIN_BG)

# -------------------------------------------------------------------------
# Create frames for the Buffers and Catering buttons + their question marks
# so we can pack them side-by-side.
# -------------------------------------------------------------------------
frame_buffers = tk.Frame(root, bg=MAIN_BG)
frame_catering = tk.Frame(root, bg=MAIN_BG)

btn_am = tk.Button(
    root,
    text="Select AM Sales CSV File",
    command=open_file_am,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG
)
btn_pm = tk.Button(
    root,
    text="Select PM Sales CSV File",
    command=open_file_pm,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG
)
btn_submit = tk.Button(
    root,
    text="Submit",
    command=submit_files,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG
)

btn_buffers = tk.Button(
    frame_buffers,
    text="Configure Buffers",
    command=open_buffer_window,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG
)
# Question mark label for Buffers
qmark_buffers = tk.Label(
    frame_buffers, text="?", bg=BTN_BG, fg=BTN_FG, width=2
)

# Attach the tooltip to the question mark
ToolTip(qmark_buffers, text="Adjust day-based % buffers (e.g. +10% on Wednesday).")

# Pack them side by side
btn_buffers.pack(side="left", padx=(0, 5))
qmark_buffers.pack(side="left")

btn_catering = tk.Button(
    frame_catering,
    text="Catering",
    command=open_catering_window,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG
)
# Question mark label for Catering
qmark_catering = tk.Label(
    frame_catering, text="?", bg=BTN_BG, fg=BTN_FG, width=2
)

ToolTip(qmark_catering, text="Adjust day-based dollar offsets (e.g. +$5 on Monday).")

btn_catering.pack(side="left", padx=(0, 5))
qmark_catering.pack(side="left")

# -------------------------------------------------------------------------
# Pack all the widgets
# -------------------------------------------------------------------------
btn_am.pack(pady=10)
btn_pm.pack(pady=10)
btn_submit.pack(pady=10)

frame_buffers.pack(pady=10)  # Holds the Buffers button + question mark
frame_catering.pack(pady=10) # Holds the Catering button + question mark

root.mainloop()
