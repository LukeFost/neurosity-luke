import json

def load_json(file_path):
    """ Load JSON data from a file. """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_json(data, file_path):
    """ Save JSON data to a file. """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def find_closest_action(timestamp, events_log):
    """ Find the closest action within a 2-second window or default to 'not_walked'. """
    closest_action = 'not_walked'
    min_diff = float('inf')
    for event in events_log:
        time_diff = abs(event['timestamp'] - timestamp)
        if time_diff < min_diff and time_diff <= 20:
            closest_action = event['action']
            min_diff = time_diff
    return closest_action

def update_classifications(events_log, raw_eeg_data):
    """ Update the classification in raw_eeg_data based on events_log actions. """
    for entry in raw_eeg_data:
        timestamp = entry.get('info', {}).get('unixTimestamp')
        if timestamp:
            closest_action = find_closest_action(timestamp, events_log)
            entry['classification'] = closest_action
    return raw_eeg_data

def main():
    # Load data
    events_log = load_json('events_log.json')
    raw_eeg_data = load_json('raw_eeg_data.json')

    # Update raw_eeg_data classifications
    updated_eeg_data = update_classifications(events_log, raw_eeg_data)

    # Save updated data
    save_json(updated_eeg_data, 'updated_raw_eeg_data.json')

if __name__ == "__main__":
    main()
