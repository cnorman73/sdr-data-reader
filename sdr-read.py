from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np

# Initialize the SDR
sdr = RtlSdr()

# Configure SDR parameters
sdr.sample_rate = 1.024e6  # 1.024 MS/s
sdr.center_freq = 915e6    # 100 MHz
sdr.gain = 10              # Gain

# Read samples
try:
    samples = sdr.read_samples(512)
    print(samples)
except rtlsdr.rtlsdr.LibUSBError as e:
    print(f"LibUSBError: {e}")

# Close the SDR connection
sdr.close()

# Use matplotlib to estimate and plot the PSD
plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate / 1e6, Fc=sdr.center_freq / 1e6)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')

plt.show()

