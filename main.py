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

API_URL = "http://127.0.0.1:5000/upload-folder"
DB_PATH = "backend/foot_data.db"

def update_bubbles(timestamp, canvas):

    results = fetch_filtered_data(timestamp)

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    bubble_locations = [
        (int(canvas_width * 0.13), int(canvas_height * 0.12), "Left_FF1"),  # Left_FF1
        (int(canvas_width * 0.207), int(canvas_height * 0.09), "Left_FF2"), # Left_FF2
        (int(canvas_width * 0.288), int(canvas_height * 0.09), "Left_FF3"),  # Left_FF3
        (int(canvas_width * 0.368), int(canvas_height * 0.12), "Left_FF4"),  # Left_FF4
        (int(canvas_width * 0.145), int(canvas_height * 0.335), "Left_MF5"), # Left_MF5
        (int(canvas_width * 0.197), int(canvas_height * 0.4), "Left_MF6"), # Left_MF6
        (int(canvas_width * 0.246), int(canvas_height * 0.335), "Left_MF7"), # Left_MF7
        (int(canvas_width * 0.3), int(canvas_height * 0.4), "Left_MF8"), # Left_MF8
        (int(canvas_width * 0.35), int(canvas_height * 0.335), "Left_MF9"), # Left_MF9
        (int(canvas_width * 0.177), int(canvas_height * 0.65), "Left_RF10"), # Left_RF10
        (int(canvas_width * 0.25), int(canvas_height * 0.6), "Left_RF11"), # Left_RF11
        (int(canvas_width * 0.325), int(canvas_height * 0.645), "Left_RF12"), # Left_RF12
        (int(canvas_width * 0.248), int(canvas_height * 0.79), "Left_RF13"), # Left_RF13

        (int(canvas_width * (0.13 + 0.5)), int(canvas_height * 0.12), "Right_FF1"),  # Right_FF1
        (int(canvas_width * (0.207 + 0.5)), int(canvas_height * 0.09), "Right_FF2"), # Right_FF2
        (int(canvas_width * (0.288 + 0.5)), int(canvas_height * 0.09), "Right_FF3"),  # Right_FF3
        (int(canvas_width * (0.368 + 0.5)), int(canvas_height * 0.12), "Right_FF4"),  # Right_FF4
        (int(canvas_width * (0.145 + 0.5)), int(canvas_height * 0.335), "Right_MF5"), # Right_MF5
        (int(canvas_width * (0.197 + 0.5)), int(canvas_height * 0.4), "Right_MF6"), # Right_MF6
        (int(canvas_width * (0.246 + 0.5)), int(canvas_height * 0.335), "Right_MF7"), # Right_MF7
        (int(canvas_width * (0.3 + 0.5)), int(canvas_height * 0.4), "Right_MF8"), # Right_MF8
        (int(canvas_width * (0.35 + 0.5)), int(canvas_height * 0.335), "Right_MF9"), # Right_MF9
        (int(canvas_width * (0.177 + 0.5)), int(canvas_height * 0.65), "Right_RF10"), # Right_RF10
        (int(canvas_width * (0.25 + 0.5)), int(canvas_height * 0.6), "Right_RF11"), # Right_RF11
        (int(canvas_width * (0.325 + 0.5)), int(canvas_height * 0.645), "Right_RF12"), # Right_RF12
        (int(canvas_width * (0.248 + 0.5)), int(canvas_height * 0.79), "Right_RF13"), # Right_RF13
    ]
    
    for x, y, name in bubble_locations:
        if name in results.columns:
            value = results[name].iloc[0]  # Extract the scalar value from the first row

            # Handle cases where the value is None or missing
            if pd.isna(value) or value is None:
                color = "grey"
            elif value < 15:
                color = "grey"
            elif 15 <= value < 151:
                color = "green"
            elif 151 <= value < 350:
                color = "yellow"
            else:
                color = "red"

            # Draw the bubble
            canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline="")
            canvas.create_text(x, y + 25, text=name, font=("Arial", 8), fill="black")

def fetch_all_timestamps():
    """
    Fetch all unique timestamps from the database.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
            SELECT DISTINCT Timestamp
            FROM (
                SELECT Timestamp FROM LeftFootData
                UNION
                SELECT Timestamp FROM RightFootData
            ) AS CombinedTimestamps
            ORDER BY Timestamp ASC;
            """
            df = pd.read_sql_query(query, conn)
        return df['Timestamp'].tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch timestamps: {e}")
        return []
    
def update_heatmap(value, canvas):
    """
    Callback function to print the timestamp corresponding to the slider value.
    """
    index = int(value)  # Convert the slider value to an integer index
    if 0 <= index < len(timestamps):
        raw_timestamp  = (timestamps[index])  # Access the corresponding timestamp from the list
        display_timestamp = raw_timestamp / 1000

        try:
            # Print timestamp
            formatted_timestamp = datetime.fromtimestamp(display_timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
            timestamp_label.config(text=formatted_timestamp, )  # Update the label to show the formatted timestamp
            update_bubbles(raw_timestamp, canvas)

        except Exception as e:
            # timestamp_label.config(text="Invalid Timestamp Format")
            print(f"{e}")
    else:
        timestamp_label.config(text="Invalid Timestamp")


# Fetch filtered data based on timestamp and selected columns
def fetch_filtered_data(timestamp):
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
    WHERE Timestamp = ?
"""          
        
            df = pd.read_sql_query(query, conn, params=(timestamp,))
        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return pd.DataFrame()


def min_max_timestamps():
    # Connect to the database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    # Query to get min and max timestamps
    query = """
        SELECT MIN(Timestamp) AS MinTimestamp, MAX(Timestamp) AS MaxTimestamp
        FROM (
            SELECT Timestamp
            FROM LeftFootData
            UNION
            SELECT Timestamp
            FROM RightFootData
        ) AS CombinedData;
    """
    
    # Execute the query and fetch results
    cursor.execute(query)
    result = cursor.fetchone()
    
    # Close the connection
    connection.close()
    
    # Return the min and max timestamps
    return result[0], result[1]


def upload_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        messagebox.showwarning("No Folder Selected", "Please select a folder to upload.")
        return

    try:
        response = requests.post(API_URL, json={"folderPath": folder_path})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Data processed and stored in SQLite.")
        else:
            messagebox.showerror("Error", f"Failed to process folder: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")

def create_gui():
    
    app = tk.Tk()
    app.title("FOCUSS APPLICATION")
    app.attributes("-fullscreen", True)
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    notebook = ttk.Notebook(app)
    notebook.pack(fill=tk.BOTH, expand=True)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    notebook.add(tab1, text="Table")
    notebook.add(tab2, text="HeatMap")

    # Heatmap Tab
    global timestamp_label, timestamps
    timestamps = sorted(fetch_all_timestamps())  # Fetch and sort all timestamps from the database
    num_timestamps = len(timestamps)

    # Timestamp Label Current Selection
    timestamp_label = tk.Label(tab2, text="", font=("Arial", 12))
    timestamp_label.pack(pady=10)
    timestamp_label.place(relx=0.5, y=(screen_height * 0.8), anchor="center")

    # Slider Style
    style = ttk.Style()
    style.configure("TScale", thickness=30)

    heatmap_slider = tk.Scale(
    tab2,
    from_=0,
    to=num_timestamps - 1,  # Each step corresponds to an index
    orient="horizontal",
    length=(screen_width // 2),  # Adjust length as needed
    resolution=1,  # Ensures integer steps
    showvalue=False,
    command=lambda value: update_heatmap(value, canvas)  # Bind slider to the update function
    )

    heatmap_slider.pack(pady=10)
    heatmap_slider.place(relx=0.5, y=(screen_height * 0.85), anchor="center") 
    
    # Load Image
    IMAGE_PATH = 'data/foot_drawn.png'
    image_width = screen_width // 2
    image_height = int(screen_height * 0.75)
    canvas = Canvas(tab2, width=image_width, height=image_height)
    canvas.pack()

    try:
        image = Image.open(IMAGE_PATH)
        image = image.resize((image_width // 2, image_height), Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)

        # Display the same image side by side
        canvas.create_image(0, 0, anchor="nw", image=photo_image)  # Left side
        canvas.create_image(image_width // 2, 0, anchor="nw", image=photo_image)  # Right side

        # Keep references to avoid garbage collection
        canvas.photo_image = photo_image
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")
        return
    
    # common buttons
    exit_button = tk.Button(app, text=" X ", command=app.destroy, bg="red", fg="white")
    exit_button.place(x=(screen_width - 50), y=20)

    upload_button = tk.Button(app, text=" Upload ", command=upload_folder, bg="black", fg="white")
    upload_button.place(x=(screen_width - 150), y=20)
    
    app.mainloop()


if __name__ == "__main__":
    create_gui()