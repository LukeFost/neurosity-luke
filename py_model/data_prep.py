import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import LSTM, Dense

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

# Define the LSTM model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(timesteps, nfeatures)))
model.add(LSTM(units=50))
model.add(Dense(units=len(np.unique(y)), activation='softmax'))  # Use the number of unique classes

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Fit the model to the training data
history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=64)

# Evaluate the model
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test accuracy: {test_accuracy}")

# Make predictions
predictions = model.predict(X_test)
