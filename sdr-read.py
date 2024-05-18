from matplotlib import mlab as mlab
from rtlsdr import RtlSdr
import numpy as np
from PIL import Image
import pygame
import time

# Increase display size by 4x
DISPLAY_WIDTH = 256 * 4
DISPLAY_HEIGHT = 200 * 4

sdr = RtlSdr()
# Configure device
sdr.sample_rate = 2.4e6  # Hz
sdr.center_freq = 915e6  # Hz
sdr.freq_correction = 60   # PPM
sdr.gain = 'auto'

# Calculate bandwidth
bandwidth = sdr.sample_rate / 2

# Calculate frequency range
lower_freq = sdr.center_freq - bandwidth / 2
upper_freq = sdr.center_freq + bandwidth / 2

print(f"Bandwidth: {bandwidth / 1e6} MHz")
print(f"Frequency range: {lower_freq / 1e6} MHz to {upper_freq / 1e6} MHz")

image = []

def get_data():
    samples = sdr.read_samples(16*1024)
    power, _ = mlab.psd(samples, NFFT=16384, Fs=sdr.sample_rate / 1e6)

    max_pow = 0
    min_pow = 10

    # Search the whole data set for maximum and minimum value
    for dat in power:
        if dat > max_pow:
            max_pow = dat
        elif dat < min_pow:
            min_pow = dat

    # Update image data
    imagelist = []
    for dat in power:
        imagelist.append(mymap(dat, min_pow, max_pow, 0, 255))
    
    # Ensure image is DISPLAY_HEIGHT in length
    imagelist = imagelist[round(len(imagelist) / 2) - round(len(imagelist) / 8): round(len(imagelist) / 2) + round(len(imagelist) / 8)]
    
    if len(image) < DISPLAY_HEIGHT:
        image.append(imagelist)
    else:
        image.pop(0)  # Remove the top row
        image.append(imagelist)  # Add the new row at the bottom

def mymap(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

pygame.init()
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH + 100, DISPLAY_HEIGHT + 50))  # Adjust display size for scales
pygame.display.set_caption("DIY SDR")
clock = pygame.time.Clock()
background = pygame.Surface(gameDisplay.get_size())
background = background.convert()
background.fill((0, 0, 0))

font = pygame.font.SysFont('Arial', 15)
game_quit = False

while not game_quit:

    gameDisplay.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_quit = True

    get_data()
    outimage = np.array(image, np.ubyte)
    outimage = Image.fromarray(outimage, mode='L')
    outimage = outimage.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.NEAREST)  # Resize the image
    outimage = outimage.convert('RGBA')
    strFormat = 'RGBA'
    raw_str = outimage.tobytes("raw", strFormat)
    surface = pygame.image.fromstring(raw_str, outimage.size, 'RGBA')
    gameDisplay.blit(surface, (50, 0))  # Adjust position for scales

    # Draw frequency scale
    for i in range(0, DISPLAY_WIDTH + 1, 256):
        freq_label = font.render(f'{94.7 + (i / DISPLAY_WIDTH) * 0.1:.2f} MHz', True, (255, 255, 255))
        gameDisplay.blit(freq_label, (i + 50, DISPLAY_HEIGHT))

    # Draw time scale
    for i in range(0, DISPLAY_HEIGHT + 1, 50):
        time_label = font.render(f'{DISPLAY_HEIGHT // 4 - i // 50} s', True, (255, 255, 255))
        gameDisplay.blit(time_label, (0, i))

    pygame.display.update()
    clock.tick(60)

pygame.quit()

try:
    pass
except KeyboardInterrupt:
    pass
finally:
    sdr.close()

