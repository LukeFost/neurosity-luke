import time
from javascript import require, On
import requests
import numpy as np
import joblib
from keras.models import load_model
import pandas as pd
from collections import Counter


mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

BOT_USERNAME = 'python'

# Load the trained LSTM model
model = load_model('lstm_model_best.keras')

# Load the scaler and encoder that were fitted on the training data
scaler = joblib.load('scaler.joblib')
encoder = joblib.load('encoder.joblib')

bot = mineflayer.createBot({
    'host': '127.0.0.1',
    'port': 25565,
    'username': BOT_USERNAME
})

bot.loadPlugin(pathfinder.pathfinder)
print("Started mineflayer")

buffer = []

def main():
    while True:
        try:
            response = requests.get('http://localhost:3001/get-eeg-data')
            if response.status_code == 200:
                eeg_data_json = response.json()
                eeg_data_df = pd.DataFrame(eeg_data_json)

                # Preprocess the data
                X = np.array(eeg_data_df['data'].tolist())  # shape: (samples, time steps, features)
                nsamples, timesteps, nfeatures = X.shape
                X_flat = X.reshape((nsamples*timesteps, nfeatures))
                X_scaled = scaler.transform(X_flat)
                X_scaled = X_scaled.reshape((nsamples, timesteps, nfeatures))

                # Append preprocessed data to buffer
                buffer.append(X_scaled)

                # Check if buffer has 40 samples
                if len(buffer) >= 2:
                    # Combine the data from buffer for classification
                    combined_data = np.concatenate(buffer, axis=0)
                    
                    # Predict the classifications with the LSTM model
                    predictions = model.predict(combined_data)
                    predicted_classes = np.argmax(predictions, axis=1)
                    predicted_labels = encoder.inverse_transform(predicted_classes)

                    # Process the classifications
                    for classification in predicted_labels:
                        print(f"Predicted classification: {classification}")

                        # Action based on classification
                    if classification == 'not_moving':
                        bot.setControlState('forward', False)
                        bot.setControlState('left', False)
                        bot.setControlState('right', False)
                    elif classification == 'walking':
                        bot.setControlState('forward', True)
                    elif classification == 'walking_left':
                        bot.setControlState('forward', True)
                        bot.setControlState('left', True)
                    elif classification == 'walking_right':
                        bot.setControlState('forward', True)
                        bot.setControlState('right', True)
                    elif classification == 'not_moving_left':
                        bot.setControlState('forward', False)
                        bot.setControlState('left', True)
                    elif classification == 'not_moving_right':
                        bot.setControlState('forward', False)
                        bot.setControlState('right', True)
                        # Add other classifications and actions as necessary

                    # Clear the buffer after processing
                    buffer.clear()

            else:
                print("Failed to retrieve EEG data")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(0.15)

if __name__ == "__main__":
    main()
