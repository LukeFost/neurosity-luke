import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load the data from the JSON file
with open('raw_eeg_data.json', 'r') as file:
    eeg_data = json.load(file)

# Extract channel names (assuming the same for all entries)
channel_names = eeg_data[0]['info']['channelNames']

# Initialize a dictionary to hold data for each channel
channel_data = {name: [] for name in channel_names}

# Process each entry in the eeg_data
for entry in eeg_data:
    classification = entry['classification']

    # Append data to each channel
    for i, channel_name in enumerate(channel_names):
        channel_data[channel_name].append((entry['data'][i], classification))

# Plotting
fig, axs = plt.subplots(len(channel_names), 1, figsize=(12, 20), sharex=True)

# Color mapping for classifications
color_map = {
    'relaxed': 'lightblue',
    'focused': 'lightgreen',
    'sleepy': 'lightcoral'
}

for i, (channel_name, data) in enumerate(channel_data.items()):
    axs[i].set_title(channel_name)
    
    start_idx = 0
    for segment, classification in data:
        end_idx = start_idx + len(segment)
        axs[i].plot(range(start_idx, end_idx), segment, color='black')
        axs[i].axvspan(start_idx, end_idx, facecolor=color_map[classification], alpha=0.3)
        start_idx = end_idx

# Add legend
relaxed_patch = mpatches.Patch(color=color_map['relaxed'], label='Relaxed')
focused_patch = mpatches.Patch(color=color_map['focused'], label='Focused')
sleepy_patch = mpatches.Patch(color=color_map['sleepy'], label='Sleepy')
plt.legend(handles=[relaxed_patch, focused_patch, sleepy_patch], loc='upper right')

plt.xlabel('Time')
plt.tight_layout()
plt.show()

fig.savefig('eeg_data_plot.png')
