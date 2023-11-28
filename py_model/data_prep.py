import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import LSTM, Dense
from kerastuner.tuners import Hyperband
import joblib

# Load the data from JSON file
data = pd.read_json('raw_eeg_data.json')

# Assuming each data entry in 'data' is a list of lists, where each inner list represents a time step
# Flatten the data to 2D for scaling (time steps * samples, features)
X = np.array(data['data'].to_list())  # shape: (samples, time steps, features)
nsamples, timesteps, nfeatures = X.shape
X_flat = X.reshape((nsamples*timesteps, nfeatures))

# Normalize the EEG data features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_flat)

# Reshape the data back to 3D after scaling
X_scaled = X_scaled.reshape((nsamples, timesteps, nfeatures))

# Encode the classifications
encoder = LabelEncoder()
y = encoder.fit_transform(data['classification'])
y_categorical = to_categorical(y)  # Use one-hot encoding for classification

# Split into train, validation, and test sets
X_train, X_temp, y_train, y_temp = train_test_split(X_scaled, y_categorical, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Define a model-building function for the tuner
def build_model(hp):
    model = Sequential()
    model.add(LSTM(units=hp.Int('units', min_value=32, max_value=256, step=32),
                   return_sequences=True,
                   input_shape=(timesteps, nfeatures)))
    model.add(LSTM(units=hp.Int('units', min_value=32, max_value=256, step=32)))
    model.add(Dense(units=hp.Int('dense_units', min_value=32, max_value=128, step=32), activation='relu'))
    model.add(Dense(units=y_categorical.shape[1], activation='softmax'))
    
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

# Initialize the tuner
tuner = Hyperband(
    build_model,
    objective='val_accuracy',
    max_epochs=10,
    hyperband_iterations=2,
    directory='hyperband',
    project_name='eeg_lstm_tuning'
)

# Perform hyperparameter tuning
tuner.search(X_train, y_train, epochs=50, validation_data=(X_val, y_val))

# Get the best hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

# Build the model with the best hyperparameters
model = build_model(best_hps)
model.summary()

# Train the best model
history = model.fit(X_train, y_train, epochs=50, validation_data=(X_val, y_val))

# Evaluate the model
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test accuracy: {test_accuracy}")

# Save the trained model and the scaler
model.save('lstm_model_best.keras')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(encoder, 'encoder.joblib')
