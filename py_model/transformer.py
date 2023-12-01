import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import MultiHeadAttention, Dense, LayerNormalization, Dropout, Embedding, Input, Flatten
from kerastuner.tuners import Hyperband
from keras.models import Model
import tensorflow as tf
import joblib
from torch import flatten

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


def positional_encoding(inputs):
    # Positional encoding for time-series data
    position = tf.range(start=0, limit=timesteps, delta=1)
    position = tf.expand_dims(position, 0)
    encoded = tf.keras.layers.Embedding(input_dim=timesteps, output_dim=nfeatures)(position)
    return inputs + encoded

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    # Attention and Feed-Forward Network for a transformer block
    x = LayerNormalization(epsilon=1e-6)(inputs)
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(x, x)
    x = Dropout(dropout)(x)
    res = x + inputs

    x = LayerNormalization(epsilon=1e-6)(res)
    x = Dense(ff_dim, activation='relu')(x)
    x = Dropout(dropout)(x)
    x = Dense(inputs.shape[-1])(x)
    return x + res

def build_transformer_model():
    inputs = Input(shape=(timesteps, nfeatures))
    
    x = positional_encoding(inputs)

    # Transformer Encoder Blocks
    for _ in range(2):  # Number of transformer blocks
        x = transformer_encoder(x, head_size=64, num_heads=4, ff_dim=64, dropout=0.1)

    # Flatten the output
    x = Flatten()(x)

    # Output layer
    outputs = Dense(y_categorical.shape[1], activation='softmax')(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Build the model with the best hyperparameters
model = build_transformer_model()
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
