import json

def write_to_json(eeg_data, file_name):
    try:
        # Read existing data from the file
        with open(file_name, 'r') as file:
            data_list = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create a new list
        data_list = []
    except json.JSONDecodeError:
        # If the file is empty or corrupted, start a new list
        data_list = []

    # Append new data
    data_list.append(eeg_data)

    # Write back to the file
    with open(file_name, 'w') as file:
        json.dump(data_list, file, indent=4)

