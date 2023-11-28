import requests
import time
import threading
import common  # Assuming this contains the write_to_csv function
from flask import Flask, request, jsonify

app = Flask(__name__)

# Shared variable for classification
current_classification = "relaxed"  # Default classification

def get_eeg_data():
    response = requests.get('http://localhost:3001/get-eeg-data')
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve data")
        return None
    
    # Function to run the main loop in a separate thread
def run_main_loop():
    last_data = None
    while True:
        eeg_data_list = get_eeg_data()  # Assuming this returns a list of dictionaries
        if eeg_data_list and eeg_data_list != last_data:
            for eeg_data in eeg_data_list:
                eeg_data['classification'] = current_classification  # Add classification to each dictionary

            print(eeg_data_list)
            common.write_to_json(eeg_data, 'raw_eeg_data.json')
            last_data = eeg_data_list
        time.sleep(0.15)


# API endpoint to update classification
@app.route('/update-classification', methods=['POST'])
def update_classification():
    global current_classification
    data = request.json
    current_classification = data.get('classification', 'relaxed')
    return jsonify({"message": f"Classification updated to {current_classification}"}), 200

# Start the main loop in a separate thread
threading.Thread(target=run_main_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(port=3002)