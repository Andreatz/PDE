import glob
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys

from PIL import Image
from decimer_segmentation import segment_chemical_structures_from_file, save_images, get_bnw_image

def chemical_structure_segmentation(input_path):
    """
    This script segments chemical structures in a document, saves the original
    segmented images as well as a binarized image and a an undistorted square
    image
    """
    # Extract chemical structure depictions and save them
    raw_segments = segment_chemical_structures_from_file(input_path)
    folder_name = os.path.splitext(input_path)[0]  # Remove file extension
    segment_dir = os.path.join(folder_name, "segments")
    save_images(
        raw_segments, segment_dir, f"{os.path.split(input_path)[1][:-4]}_orig"
    )
    # Get binarized segment images
    binarized_segments = [get_bnw_image(segment) for segment in raw_segments]
    save_images(
        binarized_segments, segment_dir, f"{os.path.split(input_path)[1][:-4]}_bnw"
    )
    # Get segments in size 400*400 and save them
    normalized_segments = [
        get_square_image(segment, 400) for segment in raw_segments
    ]
    save_images(
        normalized_segments,
        segment_dir,
        f"{os.path.split(input_path)[1][:-4]}",
    )
    print(f"Segments saved at {segment_dir}.")

    # Clean up temporary files
    for file in glob.glob(os.path.join(segment_dir, "*_orig_*.png")):
        os.remove(file)
    for file in glob.glob(os.path.join(segment_dir, "*_bnw_*.png")):
        os.remove(file)

def get_square_image(image: np.array, desired_size: int) -> np.array:
    """
    This function takes an image and resizes it without distortion
    with the result of a square image with an edge length of
    desired_size.

    Args:
        image (np.array): input image
        desired_size (int): desired output image length/height

    Returns:
        np.array: resized output image
    """
    image = Image.fromarray(image)
    old_size = image.size
    grayscale_image = image.convert("L")
    if old_size[0] or old_size[1] != desired_size:
        ratio = float(desired_size) / max(old_size)
        new_size = tuple([int(x * ratio) for x in old_size])
        grayscale_image = grayscale_image.resize(new_size, Image.LANCZOS)
    else:
        new_size = old_size
        grayscale_image = grayscale_image.resize(new_size, Image.LANCZOS)

    new_image = Image.new("L", (desired_size, desired_size))
    new_image.paste(grayscale_image, ((desired_size - new_size[0]) // 2,
                                      (desired_size - new_size[1]) // 2))
    return np.array(new_image)        

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_img.py <input_path>")
    else:
        chemical_structure_segmentation(sys.argv[1])