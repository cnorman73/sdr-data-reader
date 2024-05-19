import matplotlib.pyplot as plt
import numpy as np

# File to read the recorded data
input_file = 'segment_power_data.txt'

# Read and process the data
segments = []
with open(input_file, 'r') as f:
    lines = f.readlines()
    current_segment = []
    for line in lines:
        line = line.strip()
        if line.startswith('=== Segment Start:'):
            current_segment = []
        elif line.startswith('=== Segment End:'):
            if current_segment:
                segments.append(current_segment)
        elif line:
            parts = line.split(',')
            if len(parts) == 3:
                try:
                    current_segment.append([float(x) for x in parts])
                except ValueError:
                    print(f"Skipping malformed line: {line}")

# Plot the recorded values
plt.figure(figsize=(12, 6))
for segment in segments:
    if segment:
        times, freqs, powers = zip(*segment)
        plt.plot(times, powers, label=f'{freqs[0] / 1e6:.2f} MHz')

plt.xlabel('Time (s)')
plt.ylabel('Power (dB)')
plt.title('Recorded Power Over Time for Different Frequency Segments')
plt.legend()
plt.show()

