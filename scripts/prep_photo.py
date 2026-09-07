#!/usr/bin/env python3
"""Prep a photo for ASCII conversion: remove background, boost contrast, flatten to white."""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

SESSION = new_session("u2net")


def prep_photo(input_path: Path, output_path: Path) -> None:
    raw = input_path.read_bytes()
    cutout_bytes = remove(raw, session=SESSION)  # RGBA, background removed

    cutout = Image.open(__import__("io").BytesIO(cutout_bytes)).convert("RGBA")
    rgb = np.array(cutout.convert("RGB"))
    alpha = np.array(cutout)[:, :, 3]

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Composite onto pure white using the alpha mask so the background
    # maps to the blank end of the ASCII ramp (white -> spaces).
    white_bg = np.full_like(gray, 255)
    mask = alpha.astype(np.float32) / 255.0
    composited = (gray.astype(np.float32) * mask + white_bg.astype(np.float32) * (1 - mask)).astype(np.uint8)

    Image.fromarray(composited, mode="L").save(output_path)
    print(f"wrote {output_path}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-photo.png")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("source-prepped.png")
    prep_photo(src, dst)
