import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel, Canvas
import random
import requests
import sqlite3
import pandas as pd
import time
from datetime import datetime
import os
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from heatmap_functions import display_heatmap
from count_functions import count_overall, all_high_pressure_tables
from trends_functions import display_trends
from overview_functions import display_raw_data
from threading import Thread
import threading
import socket

if os.name == "nt":  # For Windows
    DB_PATH = os.path.join(os.path.expanduser("~"), "FOCUSS", "foot_data.db")
else:  # For Unix-based systems (Linux/Mac)
    DB_PATH = os.path.join(os.path.expanduser("~"), "FOCUSS", "foot_data.db")

def handle_upload():
    # Open a folder selection dialog
    folder_path = filedialog.askdirectory(title="Select Folder")

    # Check if a folder is selected
    if not folder_path:
        messagebox.showwarning("No Folder Selected", "Please select a folder to upload.")
        return

    # Try processing the folder
    try:
        process_folder(folder_path)
        messagebox.showinfo("Success", f"Data from {folder_path} has been processed and stored in SQLite.")
    except Exception as e:
        # Show error message if something goes wrong
        messagebox.showerror("Error", f"Failed to process folder: {e}")


def process_folder(base_folder):
    # Paths for Left Foot and Right Foot directories
    left_foot_dir = os.path.join(base_folder, "Left Foot")
    right_foot_dir = os.path.join(base_folder, "Right Foot")

    # Combine CSV files
    left_foot_data = combine_csv_files(left_foot_dir)
    right_foot_data = combine_csv_files(right_foot_dir)

    # Save to SQLite
    save_to_sqlite(left_foot_data, "LeftFootData")
    save_to_sqlite(right_foot_data, "RightFootData")


def combine_csv_files(directory):
    combined_df = pd.DataFrame()
    for file_name in os.listdir(directory):
        if file_name.endswith(".csv"):
            file_path = os.path.join(directory, file_name)
            df = pd.read_csv(file_path)
            
            # Ensure the Timestamp column exists and process it
            if "Timestamp" not in df.columns:
                raise KeyError(f"'Timestamp' column missing in file: {file_name}")
            df["Timestamp"] = pd.to_numeric(df["Timestamp"], errors="coerce") // 10  # Divide Timestamp by 10
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


def save_to_sqlite(df, table_name):
    print("Before processing columns:", df.columns.tolist())
    # df.columns = df.columns.str.replace(" ", "")
    df.columns = df.columns.map(str).str.replace(" ", "")
    print("Before processing columns:", df.columns.tolist())
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit() 


def initialize_database(DB_PATH):
    """
    Check if the database exists; if not, create it and initialize required tables.
    """
    db_folder = os.path.dirname(DB_PATH) 
     # Ensure the directory exists
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)  # Create the directory and any missing parent directories

    if not os.path.exists(DB_PATH):  # Check if the database file exists
        print("Database file not found. Creating a new database.")
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Example table creation for LeftFootData and RightFootData
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS LeftFootData (
                Timestamp INTEGER PRIMARY KEY,
                RF13 INTEGER,
                RF12 INTEGER,
                RF11 INTEGER,
                RF10 INTEGER,
                MF9 INTEGER,
                MF8 INTEGER,
                MF7 INTEGER,
                MF6 INTEGER,
                MF5 INTEGER,
                FF4 INTEGER,
                FF3 INTEGER,
                FF2 INTEGER,
                FF1 INTEGER
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS RightFootData (
                Timestamp INTEGER PRIMARY KEY,
                RF13 INTEGER,
                RF12 INTEGER,
                RF11 INTEGER,
                RF10 INTEGER,
                MF9 INTEGER,
                MF8 INTEGER,
                MF7 INTEGER,
                MF6 INTEGER,
                MF5 INTEGER,
                FF4 INTEGER,
                FF3 INTEGER,
                FF2 INTEGER,
                FF1 INTEGER
            );
            """)
            conn.commit()
            print("Database initialized with required tables.")


def create_gui():

    app = tk.Tk()
    app.title("FOCUSS APPLICATION")
    app.geometry("1200x700")  # Initial window size
    app.minsize(900, 600)  # Minimum window size
    app.configure(bg="white")

    # Enable dragging functionality
    def on_press(event):
        app.x = event.x
        app.y = event.y

    def on_drag(event):
        x = app.winfo_x() + (event.x - app.x)
        y = app.winfo_y() + (event.y - app.y)
        app.geometry(f"+{x}+{y}")

    # Bind dragging events to the title bar
    title_bar = tk.Frame(app, bg="black", relief="raised", bd=2)
    title_bar.pack(fill=tk.X)
    title_bar.bind("<ButtonPress-1>", on_press)
    title_bar.bind("<B1-Motion>", on_drag)

    # Upload button
    upload_button = tk.Button(title_bar, text=" Upload ", command=handle_upload, bg="white", fg="black", width=10)
    upload_button.pack(side=tk.LEFT, padx=10, pady=2)


    # app = tk.Tk()
    
    # # app.iconbitmap("assets/icon.ico")
    # app.title("FOCUSS APPLICATION")
    # app.attributes("-fullscreen", True)
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    app_style = ttk.Style(app)
    app_style.configure("TNotebook.Tab", font=("Arial", 16), padding=[10, 5],  background="white", 
    foreground="black")


    app_style.map(
        "TNotebook.Tab",
        background=[("selected", "lightblue")],  # Selected tab color
        foreground=[("selected", "black")]      # Selected tab text color
    )

    notebook = ttk.Notebook(app, style="TNotebook")
    notebook.pack(fill=tk.BOTH, expand=True)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)

    
    # display_count(screen_width, screen_height, tab3, DB_PATH)
    display_raw_data(tab1, DB_PATH)
    count_overall(screen_width, screen_height, tab2, DB_PATH)
    all_high_pressure_tables(screen_width, screen_height, tab3, DB_PATH)
    display_trends(screen_width, screen_height, tab4, DB_PATH)
    display_heatmap(screen_width, screen_height, tab5, DB_PATH)
    

    notebook.add(tab1, text="Raw Data")
    notebook.add(tab2, text="Summary")
    notebook.add(tab3, text="High pressure timestamps")
    notebook.add(tab4, text="Graph")
    notebook.add(tab5, text="HeatMap")
    

      # common buttons
    # exit_button = tk.Button(app, text=" X ", command=app.destroy, bg="red", fg="white")
    # exit_button.place(x=(screen_width - 50), y=10)
    # # Minimize button
    # minimize_button = tk.Button(app, text=" _ ", command=app.iconify, bg="blue", fg="white")
    # minimize_button.place(x=(screen_width - 85), y=10)

    # upload_button = tk.Button(app, text=" Upload ",  command=lambda: handle_upload(), bg="black", fg="white")
    # upload_button.place(x=(screen_width - 150), y=10)


    app.mainloop()


if __name__ == "__main__":
    initialize_database(DB_PATH)
    create_gui()
