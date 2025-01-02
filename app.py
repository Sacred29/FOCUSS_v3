# # import tkinter as tk
# # from tkinter import filedialog, messagebox, ttk
# # import requests
# # import sqlite3
# # import pandas as pd

# # # Flask API endpoint
# # API_URL = "http://127.0.0.1:5000/upload-folder"
# # DB_PATH = "backend/foot_data.db"  # SQLite database path


# # def upload_folder():
# #     # Open a folder dialog to select the base folder
# #     folder_path = filedialog.askdirectory()
# #     if not folder_path:
# #         messagebox.showwarning("No Folder Selected", "Please select a folder to upload.")
# #         return

# #     # Send the folder path to the Flask backend
# #     try:
# #         response = requests.post(API_URL, json={"folderPath": folder_path})
# #         if response.status_code == 200:
# #             messagebox.showinfo("Success", "Data processed and stored in SQLite.")
# #         else:
# #             messagebox.showerror("Error", f"Failed to process folder: {response.json().get('error', 'Unknown error')}")
# #     except Exception as e:
# #         messagebox.showerror("Error", f"Could not connect to server: {e}")


# # def display_table(tab, table_name):
# #     try:
# #         # Connect to the database and fetch data
# #         with sqlite3.connect(DB_PATH) as conn:
# #             query = f"SELECT * FROM {table_name}"
# #             df = pd.read_sql_query(query, conn)

# #         if "Timestamp" in df.columns:
# #             # Convert timestamp to human-readable format
# #             df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
# #             df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")

# #         if df.empty:
# #             messagebox.showinfo("No Data", f"No data found in table {table_name}.")
# #             return

# #         # Create Treeview for displaying the data
# #         tree = ttk.Treeview(tab, columns=list(df.columns), show="headings")
# #         for col in df.columns:
# #             tree.heading(col, text=col)
# #             tree.column(col, width=150)

# #         # Add rows to Treeview
# #         for _, row in df.iterrows():
# #             tree.insert("", tk.END, values=list(row))

# #         # Add scrollbars
# #         vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
# #         hsb = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)
# #         tree.configure(yscroll=vsb.set, xscroll=hsb.set)

# #         # Place the widgets in the tab
# #         tree.pack(fill=tk.BOTH, expand=True)
# #         vsb.pack(side=tk.RIGHT, fill=tk.Y)
# #         hsb.pack(side=tk.BOTTOM, fill=tk.X)

# #     except Exception as e:
# #         messagebox.showerror("Error", f"Failed to load table data: {e}")


# # def create_tabs(title, table_name):
# #     tab_window = tk.Toplevel()
# #     tab_window.title(f"{title} - Data Viewer")
# #     tab_window.geometry("800x600")

# #     # Create a Notebook widget for the tabs
# #     notebook = ttk.Notebook(tab_window)
# #     notebook.pack(fill=tk.BOTH, expand=True)

# #     # Create tabs
# #     tab1 = ttk.Frame(notebook)
# #     tab2 = ttk.Frame(notebook)
# #     tab3 = ttk.Frame(notebook)
# #     tab4 = ttk.Frame(notebook)

# #     # Add tabs to the notebook
# #     notebook.add(tab1, text="Table")
# #     notebook.add(tab2, text="Line Chart")
# #     notebook.add(tab3, text="Heatmap")
# #     notebook.add(tab4, text="Summary")

# #     # Display the table in the first tab
# #     display_table(tab1, table_name)


# # def create_gui():
# #     app = tk.Tk()
# #     app.title("Folder Upload and Data Viewer")
# #     app.geometry("400x300")

# #     label = tk.Label(app, text="Upload CSV Data Folder", font=("Arial", 14))
# #     label.pack(pady=10)

# #     upload_button = tk.Button(app, text="Select Folder and Upload", command=upload_folder, font=("Arial", 12))
# #     upload_button.pack(pady=10)

# #     view_left_foot_button = tk.Button(app, text="View Left Foot Data",
# #                                        command=lambda: create_tabs("Left Foot", "LeftFootData"), font=("Arial", 12))
# #     view_left_foot_button.pack(pady=5)

# #     view_right_foot_button = tk.Button(app, text="View Right Foot Data",
# #                                         command=lambda: create_tabs("Right Foot", "RightFootData"), font=("Arial", 12))
# #     view_right_foot_button.pack(pady=5)

# #     app.mainloop()


# # if __name__ == "__main__":
# #     create_gui()

# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# import requests
# import sqlite3
# import pandas as pd

# # Flask API endpoint
# API_URL = "http://127.0.0.1:5000/upload-folder"
# DB_PATH = "backend/foot_data.db"  # SQLite database path


# def upload_folder():
#     # Open a folder dialog to select the base folder
#     folder_path = filedialog.askdirectory()
#     if not folder_path:
#         messagebox.showwarning("No Folder Selected", "Please select a folder to upload.")
#         return

#     # Send the folder path to the Flask backend
#     try:
#         response = requests.post(API_URL, json={"folderPath": folder_path})
#         if response.status_code == 200:
#             messagebox.showinfo("Success", "Data processed and stored in SQLite.")
#         else:
#             messagebox.showerror("Error", f"Failed to process folder: {response.json().get('error', 'Unknown error')}")
#     except Exception as e:
#         messagebox.showerror("Error", f"Could not connect to server: {e}")


# def display_table(tab, table_name):
#     try:
#         # Connect to the database and fetch data
#         with sqlite3.connect(DB_PATH) as conn:
#             query = f"SELECT * FROM {table_name}"
#             df = pd.read_sql_query(query, conn)

#         if "Timestamp" in df.columns:
#             # Convert timestamp to human-readable format
#             df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
#             df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")

#         if df.empty:
#             messagebox.showinfo("No Data", f"No data found in table {table_name}.")
#             return

#         # Create Treeview for displaying the data
#         tree = ttk.Treeview(tab, columns=list(df.columns), show="headings")
#         for col in df.columns:
#             tree.heading(col, text=col)
#             tree.column(col, width=150)

#         # Add rows to Treeview
#         for _, row in df.iterrows():
#             tree.insert("", tk.END, values=list(row))

#         # Add scrollbars
#         vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
#         hsb = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)
#         tree.configure(yscroll=vsb.set, xscroll=hsb.set)

#         # Place the widgets in the tab
#         tree.pack(fill=tk.BOTH, expand=True)
#         vsb.pack(side=tk.RIGHT, fill=tk.Y)
#         hsb.pack(side=tk.BOTTOM, fill=tk.X)

#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to load table data: {e}")


# def display_checkboxes(tab):
#     # Example list of checkbox options
#     options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]

#     # Create a frame for the checkboxes
#     frame = tk.Frame(tab)
#     frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

#     # Create a dictionary to store checkbox variables
#     checkbox_vars = {}

#     # Dynamically generate checkboxes
#     for option in options:
#         var = tk.BooleanVar()
#         checkbox = tk.Checkbutton(frame, text=option, variable=var)
#         checkbox.pack(anchor="w", padx=5, pady=2)
#         checkbox_vars[option] = var

#     # Save selected checkboxes for future use
#     def save_selection():
#         selected = [key for key, value in checkbox_vars.items() if value.get()]
#         messagebox.showinfo("Selected Options", f"You selected: {', '.join(selected)}")

#     # Add a button to save the selections
#     save_button = tk.Button(frame, text="Save Selection", command=save_selection)
#     save_button.pack(pady=10)


# def create_tabs(title, table_name):
#     tab_window = tk.Toplevel()
#     tab_window.title(f"{title} - Data Viewer")
#     tab_window.geometry("800x600")

#     # Create a Notebook widget for the tabs
#     notebook = ttk.Notebook(tab_window)
#     notebook.pack(fill=tk.BOTH, expand=True)

#     # Create tabs
#     tab1 = ttk.Frame(notebook)
#     tab2 = ttk.Frame(notebook)
#     tab3 = ttk.Frame(notebook)
#     tab4 = ttk.Frame(notebook)
#     tab5 = ttk.Frame(notebook)  # New tab for checkboxes

#     # Add tabs to the notebook
#     notebook.add(tab1, text="Table")
#     notebook.add(tab2, text="Line Chart")
#     notebook.add(tab3, text="Heatmap")
#     notebook.add(tab4, text="Summary")
#     notebook.add(tab5, text="Checkboxes")  # Add the checkboxes tab

#     # Display the table in the first tab
#     display_table(tab1, table_name)

#     # Display checkboxes in the fifth tab
#     display_checkboxes(tab5)


# def create_gui():
#     app = tk.Tk()
#     app.title("Folder Upload and Data Viewer")
#     app.geometry("400x300")

#     label = tk.Label(app, text="Upload CSV Data Folder", font=("Arial", 14))
#     label.pack(pady=10)

#     upload_button = tk.Button(app, text="Select Folder and Upload", command=upload_folder, font=("Arial", 12))
#     upload_button.pack(pady=10)

#     view_left_foot_button = tk.Button(app, text="View Left Foot Data",
#                                        command=lambda: create_tabs("Left Foot", "LeftFootData"), font=("Arial", 12))
#     view_left_foot_button.pack(pady=5)

#     view_right_foot_button = tk.Button(app, text="View Right Foot Data",
#                                         command=lambda: create_tabs("Right Foot", "RightFootData"), font=("Arial", 12))
#     view_right_foot_button.pack(pady=5)

#     app.mainloop()


# if __name__ == "__main__":
#     create_gui()

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import sqlite3
import pandas as pd

# Flask API endpoint
API_URL = "http://127.0.0.1:5000/upload-folder"
DB_PATH = "backend/foot_data.db"  # SQLite database path


def upload_folder():
    # Open a folder dialog to select the base folder
    folder_path = filedialog.askdirectory()
    if not folder_path:
        messagebox.showwarning("No Folder Selected", "Please select a folder to upload.")
        return

    # Send the folder path to the Flask backend
    try:
        response = requests.post(API_URL, json={"folderPath": folder_path})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Data processed and stored in SQLite.")
        else:
            messagebox.showerror("Error", f"Failed to process folder: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")


def fetch_combined_data():
    """
    Fetch combined data from LeftFootData and RightFootData using an INNER JOIN on Timestamp.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # query = """
            # SELECT 
            #     l.Timestamp AS Timestamp,
            #     l.RF13 AS Left_RF13, l.RF12 AS Left_RF12, l.RF11 AS Left_RF11, l.RF10 AS Left_RF10,
            #     l.MF9 AS Left_MF9, l.MF8 AS Left_MF8, l.MF7 AS Left_MF7, l.MF6 AS Left_MF6, l.MF5 AS Left_MF5,
            #     l.FF4 AS Left_FF4, l.FF3 AS Left_FF3, l.FF2 AS Left_FF2, l.FF1 AS Left_FF1,
            #     r.RF13 AS Right_RF13, r.RF12 AS Right_RF12, r.RF11 AS Right_RF11, r.RF10 AS Right_RF10,
            #     r.MF9 AS Right_MF9, r.MF8 AS Right_MF8, r.MF7 AS Right_MF7, r.MF6 AS Right_MF6, r.MF5 AS Right_MF5,
            #     r.FF4 AS Right_FF4, r.FF3 AS Right_FF3, r.FF2 AS Right_FF2, r.FF1 AS Right_FF1
            # FROM LeftFootData l
            # INNER JOIN RightFootData r ON l.Timestamp = r.Timestamp
            # """
            query = """
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
            """
            
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch combined data: {e}")
        return pd.DataFrame()


def display_table(tab, selected_columns):
    """
    Display the table in the tab based on selected columns.
    """
    df = fetch_combined_data()

    # Filter columns based on selection
    if selected_columns:
        df = df[['Timestamp'] + selected_columns]
    
    if "Timestamp" in df.columns:
        # Convert timestamp to human-readable format
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
            df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")


    if df.empty:
        messagebox.showinfo("No Data", "No data available for the selected columns.")
        return

    # Create Treeview for displaying the data
    tree = ttk.Treeview(tab, columns=list(df.columns), show="headings")
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    # Add rows to Treeview
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))

    # Add scrollbars
    vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)

    # Place the widgets in the tab
    tree.pack(fill=tk.BOTH, expand=True)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)


# def display_checkboxes(tab, on_apply):
#     """
#     Display checkboxes for column selection.
#     """
#     options = [
#         "Left_FF1", "Left_FF2", "Left_FF3", "Left_FF4", "Left_MF5", "Left_MF6", "Left_MF7", "Left_MF8", "Left_MF9", "Left_RF10", "Left_RF11", "Left_RF12","Left_RF13", # Left foot data columns
#         "Right_FF1", "Right_FF2", "Right_FF3", "Right_FF4", "Right_MF5", "Right_MF6", "Right_MF7", "Right_MF8", "Right_MF9", "Right_RF10", "Right_RF11", "Right_RF12","Right_RF13"  # Right foot data columns
#     ]

#     # Create a frame for the checkboxes
#     frame = tk.Frame(tab)
#     frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

#     checkbox_vars = {}

#     # Dynamically generate checkboxes
#     for option in options:
#         var = tk.BooleanVar()
#         checkbox = tk.Checkbutton(frame, text=option, variable=var)
#         checkbox.pack(anchor="w", padx=5, pady=2)
#         checkbox_vars[option] = var

 # def apply_selection():
    #     # Get selected columns
    #     selected = [key for key, value in checkbox_vars.items() if value.get()]
    #     on_apply(selected)

    # # Add an Apply button to fetch and display selected data
    # apply_button = tk.Button(frame, text="Apply Selection", command=apply_selection)
    # apply_button.pack(pady=10)

def display_checkboxes(tab, on_apply):
    """
    Display checkboxes for column selection in a scrollable frame, split into Left and Right sections.
    """
    left_options = [
        "Left_FF1", "Left_FF2", "Left_FF3", "Left_FF4", 
        "Left_MF5", "Left_MF6", "Left_MF7", "Left_MF8", "Left_MF9",
        "Left_RF10", "Left_RF11", "Left_RF12", "Left_RF13"
    ]
    
    right_options = [
        "Right_FF1", "Right_FF2", "Right_FF3", "Right_FF4",
        "Right_MF5", "Right_MF6", "Right_MF7", "Right_MF8", "Right_MF9",
        "Right_RF10", "Right_RF11", "Right_RF12", "Right_RF13"
    ]

    # Create a canvas and a scrollbar for scrolling
    canvas = tk.Canvas(tab)
    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Place the canvas and scrollbar in the tab
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    checkbox_vars = {}

    # Create two frames inside the scrollable frame for Left and Right options
    left_frame = ttk.Frame(scrollable_frame)
    right_frame = ttk.Frame(scrollable_frame)

    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

    # Add checkboxes for Left options in the left frame
    for option in left_options:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(left_frame, text=option, variable=var)
        checkbox.pack(anchor="w", padx=5, pady=2)
        checkbox_vars[option] = var

    # Add checkboxes for Right options in the right frame
    for option in right_options:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(right_frame, text=option, variable=var)
        checkbox.pack(anchor="w", padx=5, pady=2)
        checkbox_vars[option] = var

    def apply_selection():
        # Get selected columns
        selected = [key for key, value in checkbox_vars.items() if value.get()]
        on_apply(selected)

    # Add an Apply button below the checkboxes
    apply_button = tk.Button(scrollable_frame, text="Apply Selection", command=apply_selection)
    apply_button.grid(row=1, column=0, columnspan=2, pady=10)

   


def create_tabs(title):
    tab_window = tk.Toplevel()
    tab_window.title(f"{title} - Data Viewer")
    tab_window.geometry("800x600")

    # Create a Notebook widget for the tabs
    notebook = ttk.Notebook(tab_window)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Create tabs
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)  # Tab for checkboxes

    # Add tabs to the notebook
    notebook.add(tab1, text="Table")
    notebook.add(tab2, text="Column Selector")

    # Display checkboxes and link to Table tab
    def refresh_table(selected_columns):
        for widget in tab1.winfo_children():
            widget.destroy()
        display_table(tab1, selected_columns)

    display_checkboxes(tab2, refresh_table)


def create_gui():
    app = tk.Tk()
    app.title("Folder Upload and Data Viewer")
    app.geometry("400x300")

    label = tk.Label(app, text="Upload CSV Data Folder", font=("Arial", 14))
    label.pack(pady=10)

    upload_button = tk.Button(app, text="Select Folder and Upload", command=upload_folder, font=("Arial", 12))
    upload_button.pack(pady=10)

    view_combined_data_button = tk.Button(app, text="View Combined Data",
                                          command=lambda: create_tabs("Combined Data"), font=("Arial", 12))
    view_combined_data_button.pack(pady=5)

    app.mainloop()


if __name__ == "__main__":
    create_gui()
