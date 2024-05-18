from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab

# Initialize the SDR
sdr = RtlSdr()

# Configure SDR parameters
sdr.sample_rate = 3.2e6  # 3.2 MS/s to cover the range properly
sdr.center_freq = 915e6  # 915 MHz (center of 914-916 MHz range)
sdr.freq_correction = 60   # PPM correction
sdr.gain = 'auto' # 10            # Gain

# Define the frequency range
freq_range = (910e6, 916e6)
chunk_size = 4096  # Increase the number of samples per chunk for better resolution

# Collect a single chunk of samples
samples = sdr.read_samples(chunk_size)

# Calculate the power spectral density (PSD) without plotting it
psd, freqs = mlab.psd(samples, NFFT=chunk_size, Fs=sdr.sample_rate)

# Adjust frequencies to account for center frequency
freqs = freqs + (sdr.center_freq - sdr.sample_rate / 2)

# Close the SDR connection
sdr.close()

# Filter the data to only include the desired frequency range
mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
filtered_freqs = freqs[mask]
filtered_psd = psd[mask]

# Plot the PSD
plt.figure(figsize=(12, 6))
plt.plot(filtered_freqs / 1e6, 10 * np.log10(filtered_psd))  # Convert frequencies to MHz
plt.xlim(910, 916)
plt.ylim(-140, 0)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (dB)')
plt.title('Power Spectral Density from 914 MHz to 916 MHz')
plt.grid(True)
plt.show()
