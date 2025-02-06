import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import time
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


def fetch_data(start_timestamp, end_timestamp, DB_PATH):
    """Fetch data efficiently using optimized SQL query."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
            SELECT
         *
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

            df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp))
            return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return pd.DataFrame()
    

def display_raw_data(tab, DB_PATH):
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

    # Grp 4: Synchronised scroll table
    def show_table():
        start_date = start_date_picker.get_date()
        start_date = datetime.combine(start_date, datetime.min.time())
        start_timestamp = int(time.mktime(start_date.timetuple())) * 1000

        end_date = end_date_picker.get_date()
        end_date = datetime.combine(end_date, datetime.min.time())
        end_timestamp = int(time.mktime((end_date + timedelta(days=1)).timetuple())) * 1000

        # selected_columns = [col for col, var in checkbox_vars.items() if var.get() == 1]
        # if not selected_columns:
        #     messagebox.showwarning("Warning", "No Sensor selected. Please select at least one sensor.")
        #     return
        df = fetch_data(start_timestamp, end_timestamp, DB_PATH)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Timestamp'] = df['Timestamp'].dt.strftime('%d-%b-%Y %H:%M:%S.%f')
        df_export = df.copy()
        df_export['Timestamp'] = " " + df_export['Timestamp']

        update_export_button(df_export, export_button, "Raw Data")

        data_columns = [col for col in df.columns if col != "Timestamp"]

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

        data_columns = [col for col in df.columns if col != "Timestamp"]

        data_tree = ttk.Treeview(
            table_frame, 
            # columns=list(df[1:].columns), 
            columns=data_columns,
            show="headings", 
            height=10
        )

        for col in data_columns:
            data_tree.heading(col, text=col)
            data_tree.column(col, anchor="center", width=100)
        data_tree.grid(row=0, column=1, sticky="nsew")
        # for col in list(df[1:].columns):
        #     data_tree.heading(col, text=col)  # Set column header to the column name
        #     data_tree.column(col, anchor="center", width=100) 

        # data_tree.grid(row=0, column=1, sticky="nsew")

        # Attach the shared vertical scrollbar
        v_scrollbar.config(command=lambda *args: (sticky_tree.yview(*args), data_tree.yview(*args)))
        sticky_tree.config(yscrollcommand=v_scrollbar.set)
        data_tree.config(yscrollcommand=v_scrollbar.set)

        # Attach the horizontal scrollbar to the data Treeview
        h_scrollbar.config(command=data_tree.xview)
        data_tree.config(xscrollcommand=h_scrollbar.set)

        for _, row in df.iterrows():
            sticky_tree.insert("", "end", values=(row["Timestamp"],))  # Only the sticky column
            # data_values = [row[col] for col in selected_columns]
            # data_tree.insert("", "end", values=data_values)
            # data_tree.insert("", tk.END, values=row[1:].tolist())
            data_tree.insert("", "end", values=[row[col] for col in data_columns])

