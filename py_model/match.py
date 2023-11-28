import pandas as pd
# Load the data with predictions
new_data_with_predictions = pd.read_json('predicted_eeg.json')

# Perform the comparison
matches = (new_data_with_predictions['classification'] == new_data_with_predictions['predicted_classification']).sum()
mismatches = (new_data_with_predictions['classification'] != new_data_with_predictions['predicted_classification']).sum()

print(f"Number of matches: {matches}")
print(f"Number of mismatches: {mismatches}")
