from flask import Flask, request, jsonify
import os
import pandas as pd
import sqlite3

app = Flask(__name__)
DB_PATH = "foot_data.db"  # SQLite database path


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
            df["Timestamp"] = df["Timestamp"] // 10  # Divide Timestamp by 10
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


def save_to_sqlite(df, table_name):
    df.columns = df.columns.str.replace(" ", "")
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


@app.route('/upload-folder', methods=['POST'])
def upload_folder():
    # Folder path is sent in request
    folder_path = request.json.get("folderPath")
    if not os.path.exists(folder_path):
        return jsonify({"error": "Folder does not exist"}), 400

    try:
        process_folder(folder_path)
        return jsonify({"message": "Data processed and stored in SQLite database."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
