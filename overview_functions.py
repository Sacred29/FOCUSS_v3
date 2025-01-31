# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk, Toplevel, Canvas, font
# from tkcalendar import DateEntry
# from datetime import datetime, timedelta
# import time
# import calendar
# import pandas as pd
# import sqlite3

# def display_raw_data(tab, DB_PATH):

#     def show_table(tab, start_date_picker, end_date_picker, DB_PATH):

#         start_date = start_date_picker.get_date()
#         start_date = datetime.combine(start_date, datetime.min.time())
#         start_timestamp = int(time.mktime(start_date.timetuple())) * 1000

#         end_date = end_date_picker.get_date()
#         end_date = datetime.combine(end_date, datetime.min.time())
#         end_timestamp = int(time.mktime((end_date + timedelta(days=1)).timetuple())) * 1000

        
        
#         df = fetch_data(start_timestamp, end_timestamp, DB_PATH)
#         df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
#         df['Timestamp'] = df['Timestamp'].dt.strftime('%d-%b-%Y %H:%M:%S.%f')
#         df_export = df
#         df_export['Timestamp'] = " " + df_export['Timestamp']

#         # update_export_button(df_export, export_button, "High Timestamps")
#         selected_columns = df.columns.tolist()[1:]

#         table_frame = ttk.Frame(tab)
#         table_frame.grid(row=1, column=0, sticky="nsew")

#         table_frame.rowconfigure(0, weight=1)
#         table_frame.columnconfigure(0, weight=0)  # Sticky table
#         table_frame.columnconfigure(1, weight=1)
        
#         v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
#         v_scrollbar.grid(row=0, column=2, sticky="ns")

#         # Horizontal scrollbar for the scrollable data columns
#         h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
#         h_scrollbar.grid(row=1, column=1, sticky="ew")

         
#         # Treeview for the sticky column
#         sticky_tree = ttk.Treeview(table_frame, columns=("Timestamp",), show="headings", height=10)
#         sticky_tree.heading("Timestamp", text="Timestamp")
#         sticky_tree.column("Timestamp", anchor="w", width=150)
#         sticky_tree.grid(row=0, column=0, sticky="nsew")

#         data_tree = ttk.Treeview(
#             table_frame, 
#             columns=tuple(selected_columns), 
#             show="headings", 
#             height=10
#         )

#         for col in selected_columns:
#             data_tree.heading(col, text=col)  # Set column header to the column name
#             data_tree.column(col, anchor="center", width=100) 

#         data_tree.grid(row=0, column=1, sticky="nsew")

#         # Attach the shared vertical scrollbar
#         v_scrollbar.config(command=lambda *args: (sticky_tree.yview(*args), data_tree.yview(*args)))
#         sticky_tree.config(yscrollcommand=v_scrollbar.set)
#         data_tree.config(yscrollcommand=v_scrollbar.set)

#         # Attach the horizontal scrollbar to the data Treeview
#         h_scrollbar.config(command=data_tree.xview)
#         data_tree.config(xscrollcommand=h_scrollbar.set)

#         for _, row in df.iterrows():
#             sticky_tree.insert("", "end", values=(row["Timestamp"],))  # Only the sticky column
#             data_values = [row[col] for col in selected_columns]
#             data_tree.insert("", "end", values=data_values)

        
        
#     control_frame = ttk.Frame(tab)
#     control_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

#     # Configure the control frame to have a fixed size and prevent expansion
#     tab.rowconfigure(0, weight=0)  # Prevent vertical expansion of controls
#     control_frame.columnconfigure(1, weight=0)  # Prevent horizontal expansion of pickers and button

#     # Start Datetime Picker
#     start_datetime_label = tk.Label(control_frame, text="From:", font=("Arial", 12))
#     start_datetime_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

#     start_date_picker = DateEntry(control_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy")
#     start_date_picker.grid(row=0, column=1, sticky="w", padx=5, pady=5)

#     # End Datetime Picker
#     end_datetime_label = tk.Label(control_frame, text="To:", font=("Arial", 12))
#     end_datetime_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)

#     end_date_picker = DateEntry(control_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy" )
#     end_date_picker.grid(row=0, column=3, sticky="w", padx=5, pady=5)

#     # Submit Button
#     submit_button = tk.Button(control_frame, text="Show Table", command=lambda: show_table(tab, start_date_picker, end_date_picker, DB_PATH))
#     submit_button.grid(row=0, column=4, sticky="w", padx=5, pady=5)
    
#     export_button = tk.Button(control_frame, text="Export CSV", state=tk.DISABLED)
#     export_button.grid(row=0, column=5, sticky="w", padx=5, pady=5)


# def fetch_data(start_timestamp, end_timestamp, DB_PATH):
#     try:
#         with sqlite3.connect(DB_PATH) as conn:
#             query = """
#     SELECT
#          *
#          FROM (
#         SELECT
#             l.Timestamp AS Timestamp,
#             l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
#             l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
#             l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
#             r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
#             r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
#             r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
#         FROM LeftFootData l
#         LEFT JOIN RightFootData r ON l.Timestamp = r.Timestamp
#         UNION
#         SELECT
#             r.Timestamp AS Timestamp,
#             l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
#             l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
#             l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
#             r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
#             r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
#             r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
#         FROM RightFootData r
#         LEFT JOIN LeftFootData l ON l.Timestamp = r.Timestamp
#     ) AS CombinedData
#     WHERE Timestamp >= ? AND Timestamp <= ?
# """

#             df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp,))

#         return df
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to fetch data: {e}")
#         return pd.DataFrame()


import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import time

def display_raw_data(tab, DB_PATH):
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


    def show_table(tab, start_date_picker, end_date_picker, DB_PATH):
        """Fetch data and display it in the table with synchronized scrolling."""
        start_date = start_date_picker.get_date()
        start_timestamp = int(time.mktime(start_date.timetuple())) * 1000

        end_date = end_date_picker.get_date()
        end_timestamp = int(time.mktime((end_date + timedelta(days=1)).timetuple())) * 1000

        # Fetch Data
        df = fetch_data(start_timestamp, end_timestamp, DB_PATH)
        if df.empty:
            messagebox.showinfo("No Data", "No records found for the selected date range.")
            return
        print(df)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Timestamp'] = df['Timestamp'].dt.strftime('%d-%b-%Y %H:%M:%S.%f')

        selected_columns = df.columns.tolist()[1:]

        # # Clear previous widgets
        # for widget in table_frame.winfo_children():
        #     widget.destroy()

        table_frame = ttk.Frame(tab)
        table_frame.grid(row=1, column=0, sticky="nsew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=0)  # Sticky table
        table_frame.columnconfigure(1, weight=1)

        # Configure Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        v_scrollbar.grid(row=0, column=2, sticky="ns")

        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.grid(row=1, column=1, sticky="ew")

        # Sticky Timestamp Column
        sticky_tree = ttk.Treeview(table_frame, columns=("Timestamp",), show="headings", height=15)
        sticky_tree.heading("Timestamp", text="Timestamp")
        sticky_tree.column("Timestamp", anchor="w", width=150)
        sticky_tree.grid(row=0, column=0, sticky="nsew")

        # Main Data Table
        data_tree = ttk.Treeview(table_frame, columns=tuple(selected_columns), show="headings", height=15)
        for col in selected_columns:
            data_tree.heading(col, text=col)
            data_tree.column(col, anchor="center", width=100)

        data_tree.grid(row=0, column=1, sticky="nsew")

        # Scrollbar Configuration
        v_scrollbar.config(command=lambda *args: (sticky_tree.yview(*args), data_tree.yview(*args)))
        sticky_tree.config(yscrollcommand=v_scrollbar.set)
        data_tree.config(yscrollcommand=v_scrollbar.set)

        h_scrollbar.config(command=data_tree.xview)
        data_tree.config(xscrollcommand=h_scrollbar.set)

        # Insert Data
        for _, row in df.iterrows():
            sticky_tree.insert("", "end", values=(row["Timestamp"],))
            data_values = [row[col] for col in selected_columns]
            data_tree.insert("", "end", values=data_values)

        # Sync scrolling
        def sync_scroll(event):
            data_tree.yview_moveto(sticky_tree.yview()[0])
        sticky_tree.bind("<MouseWheel>", sync_scroll)

    # Control Panel
    control_frame = ttk.Frame(tab)
    control_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    start_label = tk.Label(control_frame, text="From:", font=("Arial", 12))
    start_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

    start_date_picker = DateEntry(control_frame, width=12, background="darkblue", foreground="white", borderwidth=2)
    start_date_picker.grid(row=0, column=1, padx=5, pady=5)

    end_label = tk.Label(control_frame, text="To:", font=("Arial", 12))
    end_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)

    end_date_picker = DateEntry(control_frame, width=12, background="darkblue", foreground="white", borderwidth=2)
    end_date_picker.grid(row=0, column=3, padx=5, pady=5)

    submit_button = tk.Button(control_frame, text="Show Table", command=lambda: show_table(tab, start_date_picker, end_date_picker, DB_PATH))
    submit_button.grid(row=0, column=4, padx=5, pady=5)

    export_button = tk.Button(control_frame, text="Export CSV", state=tk.DISABLED)
    export_button.grid(row=0, column=5, padx=5, pady=5)

    # Table Frame
    table_frame = ttk.Frame(tab)
    table_frame.grid(row=1, column=0, sticky="nsew")
    table_frame.columnconfigure(1, weight=1)
    tab.rowconfigure(1, weight=1)

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
