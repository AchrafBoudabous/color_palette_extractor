import matplotlib
matplotlib.use('Agg')

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
import uuid

def extract_palette(image_path, num_colors=5):
    image = Image.open(image_path).convert('RGB')
    image = image.resize((150, 150))  # Speed up processing

    # Convert image data to array
    pixels = np.array(image).reshape(-1, 3)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=num_colors, n_init='auto')
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)

    # Convert to HEX
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(*color) for color in colors]

    # Create color palette image
    palette_fig = plt.figure(figsize=(num_colors, 1))
    for i, color in enumerate(colors):
        plt.fill_between([i, i+1], 0, 1, color=np.array(color)/255)
    plt.axis('off')

    # Save palette image
    palette_filename = f'static/palette_{uuid.uuid4().hex}.png'
    plt.savefig(palette_filename, bbox_inches='tight', pad_inches=0)
    plt.close(palette_fig)

    return palette_filename, hex_colors
