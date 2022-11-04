import numpy as np
import pydicom
from PIL import Image


def convert_dcm_to_png(dicom_file) -> Image:
    dicom_file = dicom_file.pixel_array.astype(float)

    rescaled_image = (np.maximum(dicom_file, 0) / dicom_file.max()) * 255 # float pixels
    final_image = np.uint8(rescaled_image) # integers pixels

    final_image = Image.fromarray(final_image)
    return final_image
