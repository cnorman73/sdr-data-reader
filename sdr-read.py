from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
from matplotlib.animation import FuncAnimation
import time
import sys

# Initialize the SDR
sdr = RtlSdr()
sdr.sample_rate = 2.4e6  # Hz
sdr.freq_correction = 60  # PPM
sdr.gain = 50  # Set gain to a higher value to capture signals

# Define frequency segments
start_freq = 902e6  # Hz
end_freq = 928e6  # Hz
segment_bw = sdr.sample_rate  # Effective bandwidth of each segment
print(f"segment bandwidth: {segment_bw}")
step_size = segment_bw / 2  # Overlap segments by half the bandwidth for smooth stitching

# Define the frequency range for the plot
freq_range = np.arange(start_freq, end_freq, step_size)

# Waterfall chart parameters
num_segments = len(freq_range)
time_window = 100  # Number of time slices to display in the waterfall chart
initial_avg_time = 5  # Initial averaging period in seconds
samples_per_avg = int(initial_avg_time * 2)  # Number of samples per frequency during initial averaging

# Initialize storage for waterfall data
waterfall_data = np.zeros((time_window, num_segments * int(segment_bw / (sdr.sample_rate / 1024))))

# Initialize storage for average power values and initial averaging flags
average_power = np.zeros(num_segments)
initial_averaging_done = [False] * num_segments
threshold = 5  # dB threshold for detecting power surge
recording = [False] * num_segments  # Flags to indicate if we are recording a segment
recording_data = []  # To store data during recording

# File to record the data
output_file = 'segment_power_data.txt'

def capture_data(center_freq, retries=5):
    attempt = 0
    while attempt < retries:
        try:
            sdr.center_freq = center_freq
            samples = sdr.read_samples(16 * 1024)
            psd, freqs = mlab.psd(samples, NFFT=16 * 1024, Fs=sdr.sample_rate)
            freqs += center_freq - sdr.sample_rate / 2  # Adjust frequencies
            return psd
        except Exception as e:
            print(f"Error capturing data: {e}")
            attempt += 1
            time.sleep(2)  # Add delay between retries
    print(f"Failed to capture data after {retries} retries")
    sys.exit(1)

# Initialize the plot
fig, ax = plt.subplots(figsize=(12, 6))
waterfall_img = ax.imshow(waterfall_data, aspect='auto', extent=[start_freq / 1e6, end_freq / 1e6, 0, time_window], cmap='viridis')
plt.colorbar(waterfall_img, ax=ax, label='Power (dB)')
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Time (s)')
ax.set_title('Waterfall Chart from 902 MHz to 928 MHz')

def update_waterfall(frame):
    global waterfall_data, average_power, recording, recording_data, initial_averaging_done
    current_data = []

    for i, freq in enumerate(freq_range):
        psd = capture_data(freq)
        psd_db = 10 * np.log10(psd)
        current_data.append(psd_db)

        # Calculate average power for this segment
        avg_power = np.mean(psd_db)

        # Initial averaging period
        if not initial_averaging_done[i]:
            if initial_avg_time > 0:
                if 'initial_averages' not in locals():
                    initial_averages = [[] for _ in range(num_segments)]
                initial_averages[i].append(avg_power)
                if len(initial_averages[i]) >= samples_per_avg:
                    average_power[i] = np.mean(initial_averages[i])
                    initial_averaging_done[i] = True
                    print(f"Initial averaging done for frequency {freq / 1e6} MHz")
            else:
                average_power[i] = avg_power
                initial_averaging_done[i] = True

        if initial_averaging_done[i]:
            # Update average power with exponential moving average
            average_power[i] = (average_power[i] * 0.99 + avg_power * 0.01)
            
            # Check if we need to start recording
            if not recording[i] and avg_power - average_power[i] > threshold:
                recording[i] = True
                with open(output_file, 'a') as f:
                    f.write(f'\n\n=== Segment Start: Frequency {freq / 1e6} MHz ===\n')
                print(f'Started recording segment at {freq / 1e6} MHz')
                recording_data.append((time.time(), freq, avg_power))
            
            # Check if we need to stop recording
            if recording[i] and avg_power - average_power[i] <= threshold:
                recording[i] = False
                with open(output_file, 'a') as f:
                    f.write(f'=== Segment End: Frequency {freq / 1e6} MHz ===\n')
                    for record in recording_data:
                        f.write(f'{record[0]},{record[1]},{record[2]}\n')
                recording_data = []
                print(f'Stopped recording segment at {freq / 1e6} MHz')

    # Concatenate the current data from all segments
    current_data = np.concatenate(current_data)

    # Ensure current_data matches the number of columns in waterfall_data
    if len(current_data) != waterfall_data.shape[1]:
        current_data = np.resize(current_data, waterfall_data.shape[1])

    # Normalize the PSD values to a fixed range for visualization
    min_val, max_val = np.min(current_data), np.max(current_data)
    current_data = np.clip(current_data, min_val, max_val)

    # Update the waterfall data
    waterfall_data = np.roll(waterfall_data, -1, axis=0)
    waterfall_data[-1, :] = current_data

    # Update the plot
    waterfall_img.set_data(waterfall_data)
    waterfall_img.set_clim(vmin=min_val, vmax=max_val)  # Set color limits
    return [waterfall_img]

# Create the animation
ani = FuncAnimation(fig, update_waterfall, interval=500, cache_frame_data=False)

# Show the plot
plt.show()

# Close the SDR connection
sdr.close()

