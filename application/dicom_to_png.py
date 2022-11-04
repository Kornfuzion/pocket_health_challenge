import numpy as np
import pydicom
from PIL import Image


def convert_dcm_to_png(file_path: str) -> Image:
    im = pydicom.dcmread(file_path)
    im = im.pixel_array.astype(float)

    rescaled_image = (np.maximum(im, 0) / im.max()) * 255 # float pixels
    final_image = np.uint8(rescaled_image) # integers pixels

    final_image = Image.fromarray(final_image)
    return final_image
