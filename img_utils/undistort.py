# MIT License
#
# Copyright (c) 2023 Yonwoo Choi, Seoul National University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import cv2
import numpy as np
import os
import glob
import argparse
from tqdm import tqdm

# Define command-line arguments
parser = argparse.ArgumentParser(description="Undistort a folder of images using pre-defined camera calibration")
parser.add_argument("--intrinsic", nargs=4, type=float, required=True, help="Camera intrinsic parameters: fx, fy, cx, cy")
parser.add_argument("--distortion", nargs='+', type=float, required=True, help="Camera distortion coefficients: k1,k2,p1,p2")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the input folder containing images to undistort")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the output folder to save undistorted images")
args = parser.parse_args()

# Parse intrinsic and distortion parameters from command-line arguments
intrinsic = np.array([
    [args.intrinsic[0], 0, args.intrinsic[2]],
    [0, args.intrinsic[1], args.intrinsic[3]],
    [0., 0., 1.]
])

distortion = np.zeros((5, 1), dtype=np.float64)

# Assign the distortion coefficients one by one
for i, coeff in enumerate(args.distortion):
    distortion[i, 0] = coeff

# Set any remaining distortion coefficients to zero
num_distortion_coeffs = len(args.distortion)
if num_distortion_coeffs < 5:
    for i in range(num_distortion_coeffs, 5):
        distortion[i] = 0


# Path to the folder containing images to undistort
input_folder = args.input_folder
output_folder = args.output_folder

# Create output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# List all image files in the folder
image_files = glob.glob(os.path.join(input_folder, '*.jpg')) + glob.glob(os.path.join(input_folder, '*.png'))

# Undistort and save images
for img_file in tqdm(image_files, desc='Undistorting images', unit='image'):
    # Read the image
    img = cv2.imread(img_file)

    # Undistort the image
    undistorted_img = cv2.undistort(img, intrinsic, distortion)

    # Save the undistorted image
    output_img_file = os.path.join(output_folder, os.path.basename(img_file))
    cv2.imwrite(output_img_file, undistorted_img)

print("Undistorted images saved to:", output_folder)
