#!/usr/bin/env python3

import os
import cv2
import numpy as np
from PIL import Image


def filter_map_pgm(
    input_pgm: str,
    output_pgm: str,
    min_obstacle_area: int = 8,
    kernel_size: int = 3,
):
    """
    Filter a ROS map .pgm file.

    Pixel convention:
        0   = occupied / obstacle
        205 = unknown
        254 = free
    """

    if not os.path.exists(input_pgm):
        raise FileNotFoundError(f"Input map does not exist: {input_pgm}")

    img = np.array(Image.open(input_pgm).convert("L"))

    occupied = (img == 0).astype(np.uint8)

    # Remove small black noise points
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        occupied,
        connectivity=8,
    )

    cleaned = np.zeros_like(occupied)

    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area >= min_obstacle_area:
            cleaned[labels == label] = 1

    # Smooth obstacle edges slightly
    if kernel_size > 1:
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    filtered = img.copy()

    # Remove original occupied cells
    filtered[img == 0] = 254

    # Add cleaned occupied cells
    filtered[cleaned == 1] = 0

    os.makedirs(os.path.dirname(output_pgm), exist_ok=True)
    Image.fromarray(filtered).save(output_pgm)

    return output_pgm


def write_filtered_yaml(
    raw_yaml_path: str,
    filtered_yaml_path: str,
    filtered_pgm_path: str,
):
    """
    Copy raw map yaml and change only the image path.
    """

    if not os.path.exists(raw_yaml_path):
        raise FileNotFoundError(f"Raw yaml does not exist: {raw_yaml_path}")

    filtered_pgm_name = os.path.basename(filtered_pgm_path)

    with open(raw_yaml_path, "r") as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        if line.strip().startswith("image:"):
            new_lines.append(f"image: {filtered_pgm_name}\n")
        else:
            new_lines.append(line)

    os.makedirs(os.path.dirname(filtered_yaml_path), exist_ok=True)

    with open(filtered_yaml_path, "w") as f:
        f.writelines(new_lines)

    return filtered_yaml_path