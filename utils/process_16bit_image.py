import numpy as np
import tqdm
import glob
from tifffile import imread, imwrite
import os
import math


def findMaxMin(I, percent):
    row, col = I.shape()
    I_sort = np.sort(I.flatten()).tolist()
    if percent == 0:
        min_v = min(I_sort)
        max_v = max(I_sort)
    else:
        min_v = I_sort[math.floor(row * col * percent)]
        max_v = I_sort[math.floor(row * col * (1 - percent))]
    return min_v, max_v


def auto_contrast(img, percent=0.001):
    img = img / 255.
    Min, Max = findMaxMin(img, percent)
    img = (img - Min) / (Max - Min)
    return img


def linear_stretch(img, min_value=0, max_value=65535, ratio=2):
    """
    线性拉伸，处理16bit数据
    """
    high_value = np.percentile(img, 100 - ratio)
    low_value = np.percentile(img, ratio)
    new_img = min_value + ((img - low_value) / (high_value - low_value)) * (max_value - min_value)
    new_img[new_img < min_value] = min_value
    new_img[new_img > max_value] = max_value
    new_img = new_img.astype(np.uint16)
    return new_img


def process_img(image_path, ratio=5):
    image = imread(image_path)[:, :, 1:]
    image = image[:, :, ::-1]
    new_image = linear_stretch(image, ratio=ratio)
    image_path = image_path[:-5] + '_%d%%_' % ratio + '16bit.tiff'
    imwrite(image_path, new_image)


if __name__ == '__main__':
    root = '/media/hb/LIU/GeoData/*/*/*/*MSS[1|2].tiff'
    tbar = tqdm.tqdm(glob.glob(root))
    for path in tbar:
        tbar.set_description('img_path:%s\n' % path)
        process_img(path)
