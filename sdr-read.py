from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
from matplotlib.animation import FuncAnimation

# Initialize the SDR
sdr = RtlSdr()
sdr.sample_rate = 2.4e6  # Hz
sdr.freq_correction = 60  # PPM
sdr.gain = 50  # Set gain to a higher value to capture signals

# Define frequency segments
start_freq = 900e6  # Hz
end_freq = 930e6  # Hz
segment_bw = sdr.sample_rate  # Effective bandwidth of each segment
step_size = segment_bw / 2  # Overlap segments by half the bandwidth for smooth stitching

# Define the frequency range for the plot
freq_range = np.arange(start_freq, end_freq, step_size)

# Waterfall chart parameters
num_segments = len(freq_range)
time_window = 100  # Number of time slices to display in the waterfall chart

# Initialize storage for waterfall data
waterfall_data = np.zeros((time_window, num_segments * int(segment_bw / (sdr.sample_rate / 1024))))

# Function to capture data for a given center frequency
def capture_data(center_freq):
    sdr.center_freq = center_freq
    samples = sdr.read_samples(16 * 1024)
    psd, freqs = mlab.psd(samples, NFFT=16 * 1024, Fs=sdr.sample_rate)
    freqs += center_freq - sdr.sample_rate / 2  # Adjust frequencies
    return psd

# Initialize the plot
fig, ax = plt.subplots(figsize=(12, 6))
waterfall_img = ax.imshow(waterfall_data, aspect='auto', extent=[start_freq / 1e6, end_freq / 1e6, 0, time_window], cmap='viridis')
plt.colorbar(waterfall_img, ax=ax, label='Power (dB)')
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Time (s)')
ax.set_title('Waterfall Chart from 900 MHz to 930 MHz')

def update_waterfall(frame):
    global waterfall_data
    # Collect data for each frequency segment
    current_data = []
    for freq in freq_range:
        psd = capture_data(freq)
        current_data.append(10 * np.log10(psd))

    # Concatenate the current data from all segments
    current_data = np.concatenate(current_data)

    # Debugging: Print min and max values of current_data
    print(f"Min value of PSD: {np.min(current_data)} dB")
    print(f"Max value of PSD: {np.max(current_data)} dB")

    # Normalize the PSD values to a fixed range for visualization
    min_val, max_val = np.min(current_data), np.max(current_data)
    current_data = np.clip(current_data, min_val, max_val)

    # Ensure current_data matches the number of columns in waterfall_data
    current_data = current_data[:waterfall_data.shape[1]]

    # Update the waterfall data
    waterfall_data = np.roll(waterfall_data, -1, axis=0)
    waterfall_data[-1, :] = current_data

    # Update the plot
    waterfall_img.set_data(waterfall_data)
    waterfall_img.set_clim(vmin=min_val, vmax=max_val)  # Set color limits
    return [waterfall_img]

# Create the animation
ani = FuncAnimation(fig, update_waterfall, interval=1000, cache_frame_data=False)

# Show the plot
plt.show()

# Close the SDR connection
sdr.close()




