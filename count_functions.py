import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel, Canvas, font
import sqlite3
import pandas as pd
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import time
import calendar
import os

def export_to_csv(df, func):
        """Export the DataFrame to the Downloads folder."""
        if df.empty:
            messagebox.showwarning("Warning", "No data available to export.")
            return

        # Get the Downloads folder path
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        timestamp = datetime.now().strftime("%d-%b-%y-%H-%M-%S")
        file_name = f"{func}_{timestamp}.csv"  # Default file name
        file_path = os.path.join(downloads_folder, file_name)

        # Save the DataFrame to the Downloads folder
        try:
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")

def update_export_button(df, button, function):
        """Update the export button with the latest DataFrame."""
        if df.empty:
            button.config(state=tk.DISABLED)  # Disable if no data
        else:
            button.config(state=tk.NORMAL, command=lambda: export_to_csv(df, function))

def count_overall(screen_width, screen_height, tab, DB_PATH):
    def show_table(tab, start_date_picker, end_date_picker, DB_PATH):
        # Process date information
        start_date = start_date_picker.get_date()
        start_date = datetime.combine(start_date, datetime.min.time())
        # start_timestamp = int(time.mktime(start_date.timetuple())) * 1000
        start_timestamp = calendar.timegm(start_date.timetuple()) * 1000 

        end_date = end_date_picker.get_date()
        end_date = datetime.combine(end_date, datetime.min.time())
        # end_timestamp = int(time.mktime((end_date + timedelta(days=1)).timetuple())) * 1000
        end_timestamp = calendar.timegm((end_date + timedelta(days=1)).timetuple()) * 1000 

        # Fetch data
        df = fetch_count_overall(start_timestamp, end_timestamp, DB_PATH)

        # Reformat the DataFrame
        df_melted = df.melt(var_name="Feature_Category", value_name="Count")
        df_melted[["Feature", "Category"]] = df_melted["Feature_Category"].str.rsplit("_", n=1, expand=True)
        df_pivot = df_melted.pivot(index="Category", columns="Feature", values="Count").fillna(0)

        # Calculate HIGH/TOTAL dynamically
        # high_total_row = (df_pivot.loc["HIGH"] / (df_pivot.loc["HIGH"] + df_pivot.loc["MEDIUM"] + df_pivot.loc["LOW"])) * 100
        denominator = df_pivot.loc["HIGH"] + df_pivot.loc["MEDIUM"] + df_pivot.loc["LOW"]
        high_total_row = (df_pivot.loc["HIGH"] / denominator) * 100
        high_total_row = high_total_row.fillna(0)
        high_total_row = high_total_row.round(2)
        high_total_row.name = "PERCENTAGE OF HIGH COUNTS/TOTAL ACTIVE DATA (%)"
        df_pivot = pd.concat([df_pivot, high_total_row.to_frame().T])

        # Reorder DF
        desired_order = ["IDLE", "LOW", "MEDIUM", "HIGH", "PERCENTAGE OF HIGH COUNTS/TOTAL ACTIVE DATA (%)"]
        df_pivot = df_pivot.reindex(desired_order)

        df_export = df_pivot.reset_index() 
        update_export_button(df_export, export_button, "Summary")  # Update export button

        # Configure grid for Treeviews
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=0)  # Fixed width for sticky index
        tab.columnconfigure(1, weight=1)  # Scrollable data column

        # Sticky index Treeview
        index_tree = ttk.Treeview(tab, columns=["Index"], show="headings", height=10)
        index_tree.grid(row=1, column=0, sticky="ns")  # Stick vertically
        index_tree.heading("Index", text="Category")
        index_tree.column("Index", anchor=tk.W, width=350)

        # Populate sticky index Treeview
        for idx in df_pivot.index:
            index_tree.insert("", tk.END, values=[idx])

        # Scrollable data Treeview
        data_tree = ttk.Treeview(tab, columns=list(df_pivot.columns), show="headings", height=10)
        data_tree.grid(row=1, column=1, sticky="nsew")  # Expandable both ways
        for col in df_pivot.columns:
            data_tree.heading(col, text=col)
            data_tree.column(col, anchor=tk.CENTER, width=100)

        # Populate scrollable data Treeview
        for _, row in df_pivot.iterrows():
            data_tree.insert("", tk.END, values=row.tolist())

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=lambda *args: [index_tree.yview(*args), data_tree.yview(*args)])
        v_scrollbar.grid(row=1, column=2, sticky="ns")

        # Horizontal scrollbar for data Treeview
        h_scrollbar = ttk.Scrollbar(tab, orient=tk.HORIZONTAL, command=data_tree.xview)
        h_scrollbar.grid(row=2, column=1, sticky="ew")

        # Configure scrollbars
        index_tree.configure(yscrollcommand=v_scrollbar.set)
        data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Synchronize vertical scrolling
        def sync_scroll(*args):
            index_tree.yview_moveto(args[0])
            data_tree.yview_moveto(args[0])

        index_tree.configure(yscrollcommand=lambda *args: sync_scroll(*args))
        data_tree.configure(yscrollcommand=lambda *args: sync_scroll(*args))

    # Group calendar pickers and button into a frame
    control_frame = ttk.Frame(tab)
    control_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    # Configure the control frame to have a fixed size and prevent expansion
    tab.rowconfigure(0, weight=0)  # Prevent vertical expansion of controls
    control_frame.columnconfigure(1, weight=0)  # Prevent horizontal expansion of pickers and button

    # Start Datetime Picker
    start_datetime_label = tk.Label(control_frame, text="From:", font=("Arial", 12))
    start_datetime_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

    start_date_picker = DateEntry(control_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy")
    start_date_picker.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # End Datetime Picker
    end_datetime_label = tk.Label(control_frame, text="To:", font=("Arial", 12))
    end_datetime_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)

    end_date_picker = DateEntry(control_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy" )
    end_date_picker.grid(row=0, column=3, sticky="w", padx=5, pady=5)

    # Submit Button
    submit_button = tk.Button(control_frame, text="Show Table", command=lambda: show_table(tab, start_date_picker, end_date_picker, DB_PATH))
    submit_button.grid(row=0, column=4, sticky="w", padx=5, pady=5)
    
    export_button = tk.Button(control_frame, text="Export CSV", state=tk.DISABLED)
    export_button.grid(row=0, column=5, sticky="w", padx=5, pady=5)

    


def fetch_count_overall(start_timestamp, end_timestamp, DB_PATH ):

    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
    SELECT
         SUM(CASE WHEN Right_FF1 < 15 THEN 1 ELSE 0 END) AS Right_FF1_IDLE,
         SUM(CASE WHEN Right_FF1 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_FF1_LOW,
         SUM(CASE WHEN Right_FF1 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_FF1_MEDIUM,
         SUM(CASE WHEN Right_FF1 > 349 THEN 1 ELSE 0 END) AS Right_FF1_HIGH,

         SUM(CASE WHEN Right_FF2 < 15 THEN 1 ELSE 0 END) AS Right_FF2_IDLE,
         SUM(CASE WHEN Right_FF2 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_FF2_LOW,
         SUM(CASE WHEN Right_FF2 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_FF2_MEDIUM,
         SUM(CASE WHEN Right_FF2 > 349 THEN 1 ELSE 0 END) AS Right_FF2_HIGH,

         SUM(CASE WHEN Right_FF3 < 15 THEN 1 ELSE 0 END) AS Right_FF3_IDLE,
         SUM(CASE WHEN Right_FF3 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_FF3_LOW,
         SUM(CASE WHEN Right_FF3 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_FF3_MEDIUM,
         SUM(CASE WHEN Right_FF3 > 349 THEN 1 ELSE 0 END) AS Right_FF3_HIGH,

         SUM(CASE WHEN Right_FF4 < 15 THEN 1 ELSE 0 END) AS Right_FF4_IDLE,
         SUM(CASE WHEN Right_FF4 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_FF4_LOW,
         SUM(CASE WHEN Right_FF4 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_FF4_MEDIUM,
         SUM(CASE WHEN Right_FF4 > 349 THEN 1 ELSE 0 END) AS Right_FF4_HIGH,

         SUM(CASE WHEN Right_MF5 < 15 THEN 1 ELSE 0 END) AS Right_MF5_IDLE,
         SUM(CASE WHEN Right_MF5 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_MF5_LOW,
         SUM(CASE WHEN Right_MF5 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_MF5_MEDIUM,
         SUM(CASE WHEN Right_MF5 > 349 THEN 1 ELSE 0 END) AS Right_MF5_HIGH,

         SUM(CASE WHEN Right_MF6 < 15 THEN 1 ELSE 0 END) AS Right_MF6_IDLE,
         SUM(CASE WHEN Right_MF6 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_MF6_LOW,
         SUM(CASE WHEN Right_MF6 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_MF6_MEDIUM,
         SUM(CASE WHEN Right_MF6 > 349 THEN 1 ELSE 0 END) AS Right_MF6_HIGH,

         SUM(CASE WHEN Right_MF7 < 15 THEN 1 ELSE 0 END) AS Right_MF7_IDLE,
         SUM(CASE WHEN Right_MF7 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_MF7_LOW,
         SUM(CASE WHEN Right_MF7 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_MF7_MEDIUM,
         SUM(CASE WHEN Right_MF7 > 349 THEN 1 ELSE 0 END) AS Right_MF7_HIGH,

         SUM(CASE WHEN Right_MF8 < 15 THEN 1 ELSE 0 END) AS Right_MF8_IDLE,
         SUM(CASE WHEN Right_MF8 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_MF8_LOW,
         SUM(CASE WHEN Right_MF8 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_MF8_MEDIUM,
         SUM(CASE WHEN Right_MF8 > 349 THEN 1 ELSE 0 END) AS Right_MF8_HIGH,

         SUM(CASE WHEN Right_MF9 < 15 THEN 1 ELSE 0 END) AS Right_MF9_IDLE,
         SUM(CASE WHEN Right_MF9 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_MF9_LOW,
         SUM(CASE WHEN Right_MF9 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_MF9_MEDIUM,
         SUM(CASE WHEN Right_MF9 > 349 THEN 1 ELSE 0 END) AS Right_MF9_HIGH,

         SUM(CASE WHEN Right_RF10 < 15 THEN 1 ELSE 0 END) AS Right_RF10_IDLE,
         SUM(CASE WHEN Right_RF10 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_RF10_LOW,
         SUM(CASE WHEN Right_RF10 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_RF10_MEDIUM,
         SUM(CASE WHEN Right_RF10 > 349 THEN 1 ELSE 0 END) AS Right_RF10_HIGH,

         SUM(CASE WHEN Right_RF11 < 15 THEN 1 ELSE 0 END) AS Right_RF11_IDLE,
         SUM(CASE WHEN Right_RF11 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_RF11_LOW,
         SUM(CASE WHEN Right_RF11 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_RF11_MEDIUM,
         SUM(CASE WHEN Right_RF11 > 349 THEN 1 ELSE 0 END) AS Right_RF11_HIGH,

         SUM(CASE WHEN Right_RF12 < 15 THEN 1 ELSE 0 END) AS Right_RF12_IDLE,
         SUM(CASE WHEN Right_RF12 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_RF12_LOW,
         SUM(CASE WHEN Right_RF12 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_RF12_MEDIUM,
         SUM(CASE WHEN Right_RF12 > 349 THEN 1 ELSE 0 END) AS Right_RF12_HIGH,

         SUM(CASE WHEN Right_RF13 < 15 THEN 1 ELSE 0 END) AS Right_RF13_IDLE,
         SUM(CASE WHEN Right_RF13 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Right_RF13_LOW,
         SUM(CASE WHEN Right_RF13 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Right_RF13_MEDIUM,
         SUM(CASE WHEN Right_RF13 > 349 THEN 1 ELSE 0 END) AS Right_RF13_HIGH,

         SUM(CASE WHEN Left_FF1 < 15 THEN 1 ELSE 0 END) AS Left_FF1_IDLE,
         SUM(CASE WHEN Left_FF1 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_FF1_LOW,
         SUM(CASE WHEN Left_FF1 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_FF1_MEDIUM,
         SUM(CASE WHEN Left_FF1 > 349 THEN 1 ELSE 0 END) AS Left_FF1_HIGH,
         
         SUM(CASE WHEN Left_FF2 < 15 THEN 1 ELSE 0 END) AS Left_FF2_IDLE,
         SUM(CASE WHEN Left_FF2 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_FF2_LOW,
         SUM(CASE WHEN Left_FF2 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_FF2_MEDIUM,
         SUM(CASE WHEN Left_FF2 > 349 THEN 1 ELSE 0 END) AS Left_FF2_HIGH,

         SUM(CASE WHEN Left_FF3 < 15 THEN 1 ELSE 0 END) AS Left_FF3_IDLE,
         SUM(CASE WHEN Left_FF3 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_FF3_LOW,
         SUM(CASE WHEN Left_FF3 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_FF3_MEDIUM,
         SUM(CASE WHEN Left_FF3 > 349 THEN 1 ELSE 0 END) AS Left_FF3_HIGH,

         SUM(CASE WHEN Left_FF4 < 15 THEN 1 ELSE 0 END) AS Left_FF4_IDLE,
         SUM(CASE WHEN Left_FF4 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_FF4_LOW,
         SUM(CASE WHEN Left_FF4 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_FF4_MEDIUM,
         SUM(CASE WHEN Left_FF4 > 349 THEN 1 ELSE 0 END) AS Left_FF4_HIGH,

         SUM(CASE WHEN Left_MF5 < 15 THEN 1 ELSE 0 END) AS Left_MF5_IDLE,
         SUM(CASE WHEN Left_MF5 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_MF5_LOW,
         SUM(CASE WHEN Left_MF5 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_MF5_MEDIUM,
         SUM(CASE WHEN Left_MF5 > 349 THEN 1 ELSE 0 END) AS Left_MF5_HIGH,

         SUM(CASE WHEN Left_MF6 < 15 THEN 1 ELSE 0 END) AS Left_MF6_IDLE,
         SUM(CASE WHEN Left_MF6 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_MF6_LOW,
         SUM(CASE WHEN Left_MF6 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_MF6_MEDIUM,
         SUM(CASE WHEN Left_MF6 > 349 THEN 1 ELSE 0 END) AS Left_MF6_HIGH,

         SUM(CASE WHEN Left_MF7 < 15 THEN 1 ELSE 0 END) AS Left_MF7_IDLE,
         SUM(CASE WHEN Left_MF7 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_MF7_LOW,
         SUM(CASE WHEN Left_MF7 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_MF7_MEDIUM,
         SUM(CASE WHEN Left_MF7 > 349 THEN 1 ELSE 0 END) AS Left_MF7_HIGH,

         SUM(CASE WHEN Left_MF8 < 15 THEN 1 ELSE 0 END) AS Left_MF8_IDLE,
         SUM(CASE WHEN Left_MF8 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_MF8_LOW,
         SUM(CASE WHEN Left_MF8 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_MF8_MEDIUM,
         SUM(CASE WHEN Left_MF8 > 349 THEN 1 ELSE 0 END) AS Left_MF8_HIGH,

         SUM(CASE WHEN Left_MF9 < 15 THEN 1 ELSE 0 END) AS Left_MF9_IDLE,
         SUM(CASE WHEN Left_MF9 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_MF9_LOW,
         SUM(CASE WHEN Left_MF9 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_MF9_MEDIUM,
         SUM(CASE WHEN Left_MF9 > 349 THEN 1 ELSE 0 END) AS Left_MF9_HIGH,

         SUM(CASE WHEN Left_RF10 < 15 THEN 1 ELSE 0 END) AS Left_RF10_IDLE,
         SUM(CASE WHEN Left_RF10 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_RF10_LOW,
         SUM(CASE WHEN Left_RF10 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_RF10_MEDIUM,
         SUM(CASE WHEN Left_RF10 > 349 THEN 1 ELSE 0 END) AS Left_RF10_HIGH,

         SUM(CASE WHEN Left_RF11 < 15 THEN 1 ELSE 0 END) AS Left_RF11_IDLE,
         SUM(CASE WHEN Left_RF11 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_RF11_LOW,
         SUM(CASE WHEN Left_RF11 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_RF11_MEDIUM,
         SUM(CASE WHEN Left_RF11 > 349 THEN 1 ELSE 0 END) AS Left_RF11_HIGH,

         SUM(CASE WHEN Left_RF12 < 15 THEN 1 ELSE 0 END) AS Left_RF12_IDLE,
         SUM(CASE WHEN Left_RF12 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_RF12_LOW,
         SUM(CASE WHEN Left_RF12 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_RF12_MEDIUM,
         SUM(CASE WHEN Left_RF12 > 349 THEN 1 ELSE 0 END) AS Left_RF12_HIGH,

         SUM(CASE WHEN Left_RF13 < 15 THEN 1 ELSE 0 END) AS Left_RF13_IDLE,
         SUM(CASE WHEN Left_RF13 BETWEEN 15 AND 150 THEN 1 ELSE 0 END) AS Left_RF13_LOW,
         SUM(CASE WHEN Left_RF13 BETWEEN 150 AND 349 THEN 1 ELSE 0 END) AS Left_RF13_MEDIUM,
         SUM(CASE WHEN Left_RF13 > 349 THEN 1 ELSE 0 END) AS Left_RF13_HIGH

         FROM (
        SELECT
            l.Timestamp AS Timestamp,
            l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
            l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
            l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
            r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
            r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
            r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
        FROM LeftFootData l
        LEFT JOIN RightFootData r ON l.Timestamp = r.Timestamp
        UNION
        SELECT
            r.Timestamp AS Timestamp,
            l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
            l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
            l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
            r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
            r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
            r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
        FROM RightFootData r
        LEFT JOIN LeftFootData l ON l.Timestamp = r.Timestamp
    ) AS CombinedData
    WHERE Timestamp >= ? AND Timestamp <= ?
"""

            df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp,))

        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return pd.DataFrame()


def all_high_pressure_tables(screen_width, screen_height, tab, DB_PATH):
    tab.rowconfigure(0, weight=0)  # First row (buttons and pickers)
    tab.rowconfigure(1, weight=1)  # Second row (table and checkboxes)
    tab.columnconfigure(0, weight=1)  # First column (table)
    tab.columnconfigure(1, weight=0)  # Second column (checkboxes)

    
    # Group 1: Date Pickers and Submit Button
    date_picker_frame = ttk.Frame(tab)
    date_picker_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)


    start_datetime_label = tk.Label(date_picker_frame, text="From:", font=("Arial", 12))
    start_datetime_label.grid(row=0, column=0, sticky="w", padx=5)

    start_date_picker = DateEntry(date_picker_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy" )
    start_date_picker.grid(row=0, column=1, sticky="w", padx=5)

    end_datetime_label = tk.Label(date_picker_frame, text="To:", font=("Arial", 12))
    end_datetime_label.grid(row=0, column=2, sticky="w", padx=5)

    end_date_picker = DateEntry(date_picker_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy")
    end_date_picker.grid(row=0, column=3, sticky="w", padx=5)

    submit_button = tk.Button(date_picker_frame, text="Show Table", command=lambda: show_table())
    submit_button.grid(row=0, column=4, sticky="w", padx=5)

    export_button = tk.Button(date_picker_frame, text="Export CSV", state=tk.DISABLED)
    export_button.grid(row=0, column=5, sticky="w", padx=5, pady=5)

    # Checkboxes
    def select_all(): 
        """Select all checkboxes."""
        for var in checkbox_vars.values():
            var.set(1)

    def remove_all():
        """Deselect all checkboxes."""
        for var in checkbox_vars.values():
            var.set(0)
            
    checkbox_frame = ttk.Frame(tab)
    checkbox_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

    # Create separate frames for Left and Right sensors within the checkbox_frame
    left_frame = ttk.Frame(checkbox_frame)
    left_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

    right_frame = ttk.Frame(checkbox_frame)
    right_frame.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

    # Sensor columns categorized
    left_sensors = [
        "Left_FF1", "Left_FF2", "Left_FF3", "Left_FF4",
        "Left_MF5", "Left_MF6", "Left_MF7", "Left_MF8", "Left_MF9",
        "Left_RF10", "Left_RF11", "Left_RF12", "Left_RF13"
    ]

    right_sensors = [
        "Right_FF1", "Right_FF2", "Right_FF3", "Right_FF4",
        "Right_MF5", "Right_MF6", "Right_MF7", "Right_MF8", "Right_MF9",
        "Right_RF10", "Right_RF11", "Right_RF12", "Right_RF13"
    ]

    # Dictionary to hold checkbox variables
    checkbox_vars = {col: tk.IntVar() for col in left_sensors + right_sensors}

    # Add checkboxes for Left sensors
    for col in left_sensors:
        cb = tk.Checkbutton(left_frame, text=col, variable=checkbox_vars[col], onvalue=1, offvalue=0)
        cb.pack(anchor="w", pady=2)

    # Add checkboxes for Right sensors
    for col in right_sensors:
        cb = tk.Checkbutton(right_frame, text=col, variable=checkbox_vars[col], onvalue=1, offvalue=0)
        cb.pack(anchor="w", pady=2)

    # Group 3: Select All and Remove All Buttons
    button_frame = ttk.Frame(tab)
    button_frame.grid(row=0, column=1, sticky="e", padx=5, pady=5)

    select_all_button = tk.Button(button_frame, text="Select All", command=select_all)
    select_all_button.pack(side="left", padx=5, pady=5)

    remove_all_button = tk.Button(button_frame, text="Remove All", command=remove_all)
    remove_all_button.pack(side="left", padx=5, pady=5)

    # Grp 4: Synchronised scroll table
    def show_table():
        start_date = start_date_picker.get_date()
        start_date = datetime.combine(start_date, datetime.min.time())
        start_timestamp = int(time.mktime(start_date.timetuple())) * 1000

        end_date = end_date_picker.get_date()
        end_date = datetime.combine(end_date, datetime.min.time())
        end_timestamp = int(time.mktime((end_date + timedelta(days=1)).timetuple())) * 1000

        selected_columns = [col for col, var in checkbox_vars.items() if var.get() == 1]
        if not selected_columns:
            messagebox.showwarning("Warning", "No Sensor selected. Please select at least one sensor.")
            return
        df = fetch_all_high_pressure(start_timestamp, end_timestamp, DB_PATH, selected_columns)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Timestamp'] = df['Timestamp'].dt.strftime('%d-%b-%Y %H:%M:%S.%f')
        df_export = df
        df_export['Timestamp'] = " " + df_export['Timestamp']

        update_export_button(df_export, export_button, "High Timestamps")
        

        table_frame = ttk.Frame(tab)
        table_frame.grid(row=1, column=0, sticky="nsew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=0)  # Sticky table
        table_frame.columnconfigure(1, weight=1)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        v_scrollbar.grid(row=0, column=2, sticky="ns")

        # Horizontal scrollbar for the scrollable data columns
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.grid(row=1, column=1, sticky="ew")

        # Treeview for the sticky column
        sticky_tree = ttk.Treeview(table_frame, columns=("Timestamp",), show="headings", height=10)
        sticky_tree.heading("Timestamp", text="Timestamp")
        sticky_tree.column("Timestamp", anchor="w", width=150)
        sticky_tree.grid(row=0, column=0, sticky="nsew")

        data_tree = ttk.Treeview(
            table_frame, 
            columns=tuple(selected_columns), 
            show="headings", 
            height=10
        )

        for col in selected_columns:
            data_tree.heading(col, text=col)  # Set column header to the column name
            data_tree.column(col, anchor="center", width=100) 

        data_tree.grid(row=0, column=1, sticky="nsew")

        # Attach the shared vertical scrollbar
        v_scrollbar.config(command=lambda *args: (sticky_tree.yview(*args), data_tree.yview(*args)))
        sticky_tree.config(yscrollcommand=v_scrollbar.set)
        data_tree.config(yscrollcommand=v_scrollbar.set)

        # Attach the horizontal scrollbar to the data Treeview
        h_scrollbar.config(command=data_tree.xview)
        data_tree.config(xscrollcommand=h_scrollbar.set)

        for _, row in df.iterrows():
            sticky_tree.insert("", "end", values=(row["Timestamp"],))  # Only the sticky column
            data_values = [row[col] for col in selected_columns]
            data_tree.insert("", "end", values=data_values)

  

def fetch_all_high_pressure(start_timestamp, end_timestamp, DB_PATH, selected_columns):
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            select_conditions = ", ".join([f"CASE WHEN {col} > 349 THEN 1 ELSE 0 END AS {col}" for col in selected_columns])

            condition = " OR ".join([f"{col} > 349" for col in selected_columns])
            
            query = f"""
    SELECT Timestamp, {select_conditions}

         FROM (
        SELECT
            l.Timestamp AS Timestamp,
            l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
            l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
            l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
            r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
            r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
            r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
        FROM LeftFootData l
        LEFT JOIN RightFootData r ON l.Timestamp = r.Timestamp
        UNION
        SELECT
            r.Timestamp AS Timestamp,
            l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
            l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
            l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
            r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
            r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
            r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
        FROM RightFootData r
        LEFT JOIN LeftFootData l ON l.Timestamp = r.Timestamp
    ) AS CombinedData
    WHERE Timestamp >= ? AND Timestamp <= ?
    AND ({condition});
"""

            df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp,))

        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return pd.DataFrame()



