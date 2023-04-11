import os
import glob
import cv2
import numpy as np 
from tqdm import tqdm

import cmath

# distorting point using first distortion parameter, in any direction
class Point2f:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def distort_point_r1(pt, k1):
    if k1 == 0:
        return pt

    if pt.y == 0:
        pt.y = 1e-5

    t2 = pt.y * pt.y
    t3 = t2 * t2 * t2
    t4 = pt.x * pt.x
    t7 = k1 * (t2 + t4)

    if k1 > 0:
        t8 = 1.0 / t7
        t10 = t3 / (t7 * t7)
        t14 = cmath.sqrt(t10 * (0.25 + t8 / 27.0))
        t15 = t2 * t8 * pt.y * 0.5
        t17 = pow(t14 + t15, 1.0 / 3.0)
        t18 = t17 - t2 * t8 / (t17 * 3.0)
        return Point2f(t18 * pt.x / pt.y, t18)
    else:
        t9 = t3 / (t7 * t7 * 4.0)
        t11 = t3 / (t7 * t7 * t7 * 27.0)
        t12 = t9 + t11
        t13 = cmath.sqrt(t12)
        t14 = t2 / t7
        t15 = t14 * pt.y * 0.5
        t16 = t13 + t15
        t17 = pow(t16, 1.0 / 3.0)
        t18 = (t17 + t14 / (t17 * 3.0)) * cmath.sqrt(3.0) * 1j
        t19 = -0.5 * (t17 + t18) + t14 / (t17 * 6.0)
        return Point2f(t19.real * pt.x / pt.y, t19.real)

# Read camera parameters from the given file
def read_camera_params(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("1"):
            # Extract camera parameters from the line
            _, _, _, _, fx, fy, cx, cy, k1, k2, p1, p2 = line.split()
            fx, fy, cx, cy, k1, k2, p1, p2 = map(float, (fx, fy, cx, cy, k1, k2, p1, p2))

    return fx, fy, cx, cy, k1, k2, p1, p2

# Undistort images in the input folder and save them to the output folder
def undistort_images(input_folder, output_folder, camera_params):
    fx, fy, cx, cy, k1, k2, p1, p2 = camera_params
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0, 0, 1]])
    dist_coeffs = np.array([k1, k2, p1, p2])

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through all files in the input folder
    for root, _, files in os.walk(input_folder):
        for file in tqdm(files, desc=f'Undistorting {input_folder}...'):
            if file.endswith('.jpg'):
                img_path = os.path.join(root, file)
                img = cv2.imread(img_path)

                h, w = img.shape[:2]

                # Undistort the image using the camera parameters
                undistorted_img = cv2.undistort(img, K, dist_coeffs)
                
                # Save the undistorted image to the output folder
                output_img_path = os.path.join(output_folder, file)
                cv2.imwrite(output_img_path, undistorted_img)

def main():
    camera_params_file = 'colmap_data/sparse/0/converter/cameras.txt'
    base_input_folder = 'preprocessed'
    subfolders = ['scene']

    # Read camera parameters from the file
    camera_params = read_camera_params(camera_params_file)

    # Undistort images in all subfolders
    for subfolder in subfolders:
        input_folder = os.path.join(base_input_folder, subfolder)
        output_folder = os.path.join(base_input_folder, 'undistorted_' + subfolder)
        undistort_images(input_folder, output_folder, camera_params)


if __name__ == '__main__':
    main()
