import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel, Canvas, font
import sqlite3
import pandas as pd
from tkcalendar import DateEntry
from datetime import datetime, timedelta, timezone
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter, HourLocator
import pytz
import os

def gen_time_intervals():
    times = []
    for hour in range(24):
        for minute in (0, 30):  # 0 and 30 minutes
            period = "AM" if hour < 12 else "PM"
            display_hour = hour % 12 or 12  # Convert 0 to 12 for 12-hour format
            times.append(f"{display_hour}:{minute:02} {period}")
    return times

def display_trends(screen_width, screen_height, tab, DB_PATH):
    get_trend(tab, DB_PATH)

def get_trend(tab, DB_PATH):
    global current_fig 
    current_fig = None

    tab.rowconfigure(0, weight=0) 
    tab.rowconfigure(1, weight=1)  
    tab.columnconfigure(0, weight=1)  
    tab.columnconfigure(1, weight=0)

    date_picker_frame = ttk.Frame(tab)
    date_picker_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    start_datetime_label = tk.Label(date_picker_frame, text="Start datetime:", font=("Arial", 12))
    start_datetime_label.grid(row=0, column=0, sticky="w", padx=5)

    start_date_picker = DateEntry(date_picker_frame, width=15, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yy" )
    start_date_picker.grid(row=0, column=1, sticky="w", padx=5)

    time_intervals = gen_time_intervals()
    time_dropdown = ttk.Combobox(date_picker_frame, values=time_intervals, state="readonly", width=15)
    time_dropdown.grid(row=0, column=2, sticky="w", padx=5)
    time_dropdown.set("07:00 AM")

    tk.Label(date_picker_frame, text="Duration (Hours):", font=("Arial", 12)).grid(row=0, column=3, sticky="w", padx=5)
    duration_dropdown = ttk.Combobox(date_picker_frame, values=list(range(1, 25)), width=5, justify="center")
    duration_dropdown.set("1")  # Default value
    duration_dropdown.grid(row=0, column=4, sticky="w", padx=5)

    submit_button = tk.Button(date_picker_frame, text="Show Graph", command=lambda: show_trend())
    submit_button.grid(row=0, column=5, sticky="e", padx=5, pady=5)

    export_button = tk.Button(date_picker_frame, text="Export Graph", state="disabled", command=lambda: save_graph())
    export_button.grid(row=0, column=6, sticky="e", padx=10, pady=10)

    
    
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

   
    
    # Table
    
    def show_trend():
        global current_fig 

        selected_columns = [col for col, var in checkbox_vars.items() if var.get() == 1]
        if not selected_columns:
            messagebox.showwarning("Warning", "No Sensor selected. Please select at least one sensor.")
            return
        selected_date = start_date_picker.get()
        selected_time = time_dropdown.get()
        datetime_str = f"{selected_date} {selected_time}"
        selected_date_time_obj = datetime.strptime(datetime_str, "%d/%m/%y %I:%M %p").replace(tzinfo=timezone.utc)
        start_timestamp = int(selected_date_time_obj.timestamp()) *1000
        end_date_time_obj = selected_date_time_obj + timedelta(hours=int(duration_dropdown.get()))
        end_timestamp =  int(end_date_time_obj.timestamp()) *1000
        
        df = fetch_24hour_data(start_timestamp, end_timestamp, DB_PATH)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        fig, ax = plt.subplots(figsize=(14, 8))  # Adjusted size for better fit

        # Plot only selected sensors
        for sensor in selected_columns:
            if sensor in df.columns:
                ax.plot(df['Timestamp'], df[sensor], label=sensor)
        
    
        ax.xaxis.set_major_locator(HourLocator(interval=max(1, int(duration_dropdown.get()) // 12)))  # Show label every hour for <= 12 hours. else every 2 hours
        ax.xaxis.set_major_formatter(DateFormatter('%d-%b-%y %H:%M'))  # Format as HH:MM
        ax.tick_params(axis='x', rotation=45) 
        ax.set_xlim(pd.to_datetime(start_timestamp, unit='ms'), pd.to_datetime(end_timestamp, unit='ms'))  # Set x-axis range
        ax.set_xlabel("Time")
        ax.set_ylabel("Sensor Value (kPa)")
        ax.set_title(f"Sensor Data Over {int(duration_dropdown.get())} Hours from {pd.to_datetime(start_timestamp, unit='ms').strftime('%d-%b-%y %H:%M')} to {pd.to_datetime(end_timestamp, unit='ms').strftime('%d-%b-%y %H:%M')}")

        fig.tight_layout()
        ax.legend(loc='best', fontsize='small') 
        ax.grid()
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=1, column=0, padx=10, pady=10)  # Embed at grid(row=1, column=0)
        canvas.draw()
        
        current_fig = fig  # Update the global figure variable
        export_button.config(state="normal")

    def save_graph():
        global current_fig 
        # Get the user's Downloads folder path
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_folder):
            os.makedirs(downloads_folder)  # Create the folder if it doesn't exist (just in case)

        # Generate a default filename with a timestamp
        timestamp = datetime.now().strftime("%d-%b-%y-%H-%M-%S")
        file_path = os.path.join(downloads_folder, f"Sensor_Graph_{timestamp}.png")

        try:
            current_fig.savefig(file_path)
            messagebox.showinfo("Success", f"Graph saved in {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph: {e}")
        # export_button = tk.Button(date_picker_frame, text="Export Graph to Downloads", command=save_graph)
        # # export_button.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        # # export_button.pack(side="left", padx=5, pady=5)
        # export_button.grid(row=0, column=6, sticky="e", padx=5, pady=5)
        

        

def fetch_24hour_data(start_timestamp, end_timestamp, DB_PATH):
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

            df = pd.read_sql_query(query, conn, params=(start_timestamp, end_timestamp,))

        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return pd.DataFrame()

