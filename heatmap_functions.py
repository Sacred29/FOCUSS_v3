import tkinter as tk
import pandas as pd
from tkinter import filedialog, messagebox, ttk, Toplevel, Canvas
import sqlite3
import os
import sys
from PIL import Image, ImageTk
from datetime import datetime

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def display_heatmap(screen_width, screen_height, tab, DB_PATH): 
    # Configure grid layout for the tab
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)


    # Canvas dimensions
    canvas_width = screen_width // 4
    canvas_height = int(screen_height * 0.75)

    # Create a canvas to hold both images and bubbles
    canvas = Canvas(tab, width=canvas_width * 2, height=canvas_height, bg="white")
    canvas.grid(row=0, column=0, padx=10, pady=10)

    # Load and place the image
    IMAGE_PATH = resource_path('assets/foot_drawn.png')
    try:
        # Load and resize the image
        image = Image.open(IMAGE_PATH).resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage for Tkinter
        photo_image = ImageTk.PhotoImage(image)

        # Place the image twice on the canvas
        canvas.create_image(0, 0, anchor="nw", image=photo_image)  # Left image
        canvas.create_image(canvas_width, 0, anchor="nw", image=photo_image)  # Right image

        # Keep a reference to avoid garbage collection
        canvas.photo_image = photo_image
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")
        return
    
    
    # Slider for timestamp selection
    timestamps = sorted(fetch_all_timestamps(DB_PATH))
    num_timestamps = len(timestamps)

    # heatmap_slider.grid(row=2, column=1, padx=10, pady=5, sticky="w")  

     # Add a legend for the pressure ranges below the canvas
    legend_frame = tk.Frame(tab)
    legend_frame.grid(row=0, column=1, padx=5)

    tk.Label(legend_frame, text="Pressure Colour (kPA)", font=("Arial", 26, "bold")).grid(row=0, column=0, pady=5, columnspan=2)

    # Define the legend details
    legend_items = [
        ("< 15 or N/A", "grey"),
        ("15 - 150", "green"),
        ("151 - 349", "yellow"),
        ("350+", "red"),
    ]

    # Add legend items
    for i, (label, color) in enumerate(legend_items, start=1):
        # Create a colored oval
        legend_canvas = tk.Canvas(legend_frame, width=40, height=40, bg="white", highlightthickness=0)
        legend_canvas.create_oval(4, 4, 36, 36, fill=color, outline="")
        legend_canvas.grid(row=i, column=0, padx=(5,10), pady=2)

        # Add a text label for the range
        tk.Label(legend_frame, text=label, font=("Arial", 24)).grid(row=i, column=1, padx=(0,10), sticky="w")

    # Play Button
    # Variable to track play/pause state
    is_playing = [False]  # Use a mutable object to allow modifications inside functions

    # Function to control playback
    def toggle_play_pause(slider, timestamps, canvas, label, DB_PATH, button):
        if is_playing[0]:  # If currently playing
            is_playing[0] = False
            button.config(text="Play")
        else:  # If paused
            is_playing[0] = True
            button.config(text="Pause")
            play(slider, timestamps, canvas, label, DB_PATH, button)

    # Function to play through the timestamps
    def play(slider, timestamps, canvas, label, DB_PATH, button):
        if not is_playing[0]:  # Stop if paused
            return

        # Get current slider value
        current_value = slider.get()

        # Move to the next value if within range
        if current_value < len(timestamps) - 1:
            slider.set(current_value + 1)
            update_heatmap(current_value + 1, canvas, label, timestamps, DB_PATH)
            tab.after(500, lambda: play(slider, timestamps, canvas, label, DB_PATH, button))  # Delay of 500ms
        else:
            # Stop when reaching the end
            is_playing[0] = False
            button.config(text="Play")


    
    # play_pause_button.grid(row=2, column=0, padx=10)
    # heatmap_slider.grid(row=2, column=1, padx=10, sticky="w")


    
        # Frame for Play button and slider
    control_frame = tk.Frame(tab)
    control_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="n")

    timestamp_label = tk.Label(control_frame, text="", font=("Arial", 12))
    timestamp_label.grid(row=0, column=0, columnspan=2, pady=5) 
    # Play/Pause Button
    play_pause_button = tk.Button(
        control_frame,
        text="Play",
        font=("Arial", 12),
        command=lambda: toggle_play_pause(
            heatmap_slider, timestamps, canvas, timestamp_label, DB_PATH, play_pause_button
        ),
    )
    play_pause_button.grid(row=1, column=0)

    # Slider for timestamp selection
    heatmap_slider = tk.Scale(
        control_frame,
        from_=0,
        to=num_timestamps - 1,
        orient="horizontal",
        length=400,  # Adjust length as needed
        resolution=1,
        showvalue=False,
        command=lambda value: update_heatmap(value, canvas, timestamp_label, timestamps, DB_PATH),
    )
    heatmap_slider.set(0)
    tab.after(100, lambda: update_heatmap(0, canvas, timestamp_label, timestamps, DB_PATH))
    heatmap_slider.grid(row=1, column=1, sticky="w")  # No padding, directly adjacent


def update_bubbles(timestamp, canvas, DB_PATH):
    # Clear all bubbles (but keep the images)
    canvas.delete("bubble")

    # Fetch data for the given timestamp
    results = fetch_filtered_data(timestamp, DB_PATH)

    # Use consistent dimensions for bubble placement
    canvas_width = canvas.winfo_reqwidth()  # Use the initially requested width of the Canvas
    canvas_height = canvas.winfo_reqheight()  # Use the initially requested height of the Canvas

    bubble_locations = [
        (int(canvas_width * 0.13), int(canvas_height * 0.12), "Left_FF1"),  # Left_FF1
        (int(canvas_width * 0.207), int(canvas_height * 0.09), "Left_FF2"),  # Left_FF2
        (int(canvas_width * 0.288), int(canvas_height * 0.09), "Left_FF3"),  # Left_FF3
        (int(canvas_width * 0.368), int(canvas_height * 0.12), "Left_FF4"),  # Left_FF4
        (int(canvas_width * 0.145), int(canvas_height * 0.335), "Left_MF5"),  # Left_MF5
        (int(canvas_width * 0.197), int(canvas_height * 0.4), "Left_MF6"),  # Left_MF6
        (int(canvas_width * 0.246), int(canvas_height * 0.335), "Left_MF7"),  # Left_MF7
        (int(canvas_width * 0.3), int(canvas_height * 0.4), "Left_MF8"),  # Left_MF8
        (int(canvas_width * 0.35), int(canvas_height * 0.335), "Left_MF9"),  # Left_MF9
        (int(canvas_width * 0.177), int(canvas_height * 0.65), "Left_RF10"),  # Left_RF10
        (int(canvas_width * 0.25), int(canvas_height * 0.6), "Left_RF11"),  # Left_RF11
        (int(canvas_width * 0.325), int(canvas_height * 0.645), "Left_RF12"),  # Left_RF12
        (int(canvas_width * 0.248), int(canvas_height * 0.79), "Left_RF13"),  # Left_RF13

        (int(canvas_width * (0.13 + 0.5)), int(canvas_height * 0.12), "Right_FF1"),  # Right_FF1
        (int(canvas_width * (0.207 + 0.5)), int(canvas_height * 0.09), "Right_FF2"),  # Right_FF2
        (int(canvas_width * (0.288 + 0.5)), int(canvas_height * 0.09), "Right_FF3"),  # Right_FF3
        (int(canvas_width * (0.368 + 0.5)), int(canvas_height * 0.12), "Right_FF4"),  # Right_FF4
        (int(canvas_width * (0.145 + 0.5)), int(canvas_height * 0.335), "Right_MF5"),  # Right_MF5
        (int(canvas_width * (0.197 + 0.5)), int(canvas_height * 0.4), "Right_MF6"),  # Right_MF6
        (int(canvas_width * (0.246 + 0.5)), int(canvas_height * 0.335), "Right_MF7"),  # Right_MF7
        (int(canvas_width * (0.3 + 0.5)), int(canvas_height * 0.4), "Right_MF8"),  # Right_MF8
        (int(canvas_width * (0.35 + 0.5)), int(canvas_height * 0.335), "Right_MF9"),  # Right_MF9
        (int(canvas_width * (0.177 + 0.5)), int(canvas_height * 0.65), "Right_RF10"),  # Right_RF10
        (int(canvas_width * (0.25 + 0.5)), int(canvas_height * 0.6), "Right_RF11"),  # Right_RF11
        (int(canvas_width * (0.325 + 0.5)), int(canvas_height * 0.645), "Right_RF12"),  # Right_RF12
        (int(canvas_width * (0.248 + 0.5)), int(canvas_height * 0.79), "Right_RF13"),  # Right_RF13
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
            canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline="", tags="bubble")
            canvas.create_text(x, y + 25, text=name, font=("Arial", 8), fill="black", tags="bubble")


# Fetch filtered data based on timestamp and selected columns
def fetch_filtered_data(timestamp, DB_PATH):
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
    

def fetch_all_timestamps(DB_PATH):
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

def update_heatmap(value, canvas, timestamp_label, timestamps, DB_PATH):
    """
    Callback function to print the timestamp corresponding to the slider value.
    """
    index = int(value)  # Convert the slider value to an integer index
    if 0 <= index < len(timestamps):
        raw_timestamp  = (timestamps[index])  # Access the corresponding timestamp from the list
        # display_timestamp = raw_timestamp /1000

        try:
            # Print timestamp
            
            # formatted_timestamp = datetime.fromtimestamp(display_timestamp).strftime("%d-%b-%y %H:%M:%S.%f")
            timestamp_label.config(text=pd.to_datetime(raw_timestamp,  unit='ms').strftime("%d-%b-%y %H:%M:%S.%f"))  # Update the label to show the formatted timestamp
            update_bubbles(raw_timestamp, canvas, DB_PATH)

        except Exception as e:
            # timestamp_label.config(text="Invalid Timestamp Format")
            print(f"{e}")
    else:
        timestamp_label.config(text="Invalid Timestamp")

