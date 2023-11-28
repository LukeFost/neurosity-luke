import requests

def get_eeg_data():
    response = requests.get('http://localhost:3001/get-eeg-data')
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve data")
        return None

# Example usage
eeg_data = get_eeg_data()
if eeg_data:
    print(eeg_data)
