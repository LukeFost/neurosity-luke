import numpy as np
import pandas as pd
import joblib
from keras.utils import to_categorical
from keras.models import load_model

# Load the trained LSTM model
model = load_model('lstm_model.keras')

# Load the scaler and encoder that were fitted on the training data
scaler = joblib.load('scaler.joblib')
encoder = joblib.load('encoder.joblib')

# Load the new data from JSON file
new_data = pd.read_json('cleaned_normalized_eeg_data.json')

# Preprocess the new data, similar to how the training data was preprocessed
# Flatten the data to 2D for scaling (time steps * samples, features)
X_new = np.array(new_data['data'].to_list())  # shape: (samples, time steps, features)
nsamples, timesteps, nfeatures = X_new.shape
X_new_flat = X_new.reshape((nsamples*timesteps, nfeatures))

# Use the previously fitted scaler to transform the new data
X_new_scaled = scaler.transform(X_new_flat)

# Reshape the data back to 3D after scaling
X_new_scaled = X_new_scaled.reshape((nsamples, timesteps, nfeatures))

# Assuming that the new data also contains classifications
# Transform the new classifications using the previously fitted encoder
y_new = encoder.transform(new_data['classification'])
y_new_categorical = to_categorical(y_new)

# Predict the classifications with the LSTM model
predictions_new = model.predict(X_new_scaled)

# Transform predictions back to label encoding
predicted_classes = np.argmax(predictions_new, axis=1)
predicted_labels = encoder.inverse_transform(predicted_classes)

# Add the predicted classifications to the DataFrame
new_data['predicted_classification'] = predicted_labels

# Save the updated DataFrame with predictions to a new JSON file
new_data.to_json('predicted_eeg.json', orient='records')
