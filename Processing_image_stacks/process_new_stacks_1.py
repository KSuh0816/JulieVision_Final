
# This is the FRM script to use your trained weights and process new images in a folder. 

# ------------------------------------------------------------------

# Set your parameters here and run it:


# Path to raw input/output TIFF files: 
input_dir = '/scratch/gpfs/ksuh/Elena/1/'
output_dir = '/scratch/gpfs/ksuh/Elena/Result/'

# Path to working directory (where weights/stats are saved):
working_dir = '/home/ksuh/JulieVision8bitCrop/NikonWeightDec21/'

# Weights file name:
weights_file = 'Nikon_4X_Kevin_Dec21_weights.h5'

# Stats file name (if unsure, leave as is):
stats_name = 'stats_data.npy'

# ------------------------------------------------------------------

# Imports:

# added: 
from skimage import io
from tifffile import imsave

import os
import sys
import random
import warnings
import numpy as np
import time
from PIL import Image
from libtiff import TIFF
import keras
from keras import optimizers
from keras.models import Model, load_model
from keras.layers import Input
from keras.layers.core import Dropout, Lambda
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D
from keras.layers.merge import concatenate
from keras import backend as K
import tensorflow as tf

from source import frm_models

t = time.time()

# ------------------------------------------------------------------

# Create output directory if it doesn't exist:
if not os.path.exists(output_dir):
    # Creating output directory:
    os.makedirs(output_dir)

# Get normalization parameters:
stats_data = np.load(working_dir + stats_name)
in_mean = stats_data[0]
in_stdev = stats_data[1]
out_mean = stats_data[2]
out_stdev = stats_data[3]

# Get the model:
model = frm_models.get_unet(256, 256, 1)

# Model parameters and optimization settings:
adad = keras.optimizers.Adadelta(lr=1.0, rho=0.95, epsilon=None, decay=0.0)
loss_func = 'mean_squared_error'
weights_file = working_dir + weights_file

# Compile model: 
model.compile(loss=loss_func,
          optimizer=adad,
          metrics=['mse'])
# Load weights
model.load_weights(weights_file, by_name=True)

# ------------------------------------------------------------------

Image.MAX_IMAGE_PIXELS = None

# A helper function to get all the files in a directory. 
def get_file_list_from_dir(datadir):
    all_files = os.listdir(os.path.abspath(datadir))
    data_files = list(filter(lambda file: file.endswith('.tif'), all_files))
    return data_files

# Helper functions for processing the input image: 
def sliding_window(image, stepSize, windowSize, imgarr, nucmap, covmap, inner_mat, outer_mat):
        # slide a window across the image
        for y in range(0, h-3*stepSize, stepSize):
                for x in range(0, w-3*stepSize, stepSize):
                        # process the current window
                        window_chunk = imgarr[:, y:y + windowSize[1], x:x + windowSize[0], :]
                        predict_chunk = model.predict(window_chunk, verbose=0)[0,:,:,0]
                        predict_reduced = np.zeros((256, 256), dtype=np.float64)
                        predict_reduced[int(256/4):int(3*256/4), int(256/4):int(3*256/4)] = predict_chunk[int(256/4):int(3*256/4), int(256/4):int(3*256/4)]    
                        nucmap[y:y + windowSize[1], x:x + windowSize[0]] += predict_reduced
                        covmap[y:y + windowSize[1], x:x + windowSize[0]] += outer_mat
        return nucmap, covmap

def process_one_image(impath, i, j, img, h, w, pred_img, model, stepSize, windowSize, output_mean, output_stdev, img_shape, bord):
    # Initialize arrays: 
    imgarr = np.zeros((1, h, w, 1), dtype=np.float64)
    imgarr[0,:,:,0] = img
    nucmap = np.zeros((h, w), dtype=np.float64)
    covmap = np.zeros((h, w), dtype=np.float64)
    inner_mat = np.ones((int(bord*2), int(bord*2)))
    outer_mat = np.pad(inner_mat, ((int(bord), int(bord)), (int(bord), int(bord))), 'constant', constant_values=(0, 0))

    # Process each patch in a sliding-window fasion:
    nucmap, covmap = sliding_window(img, stepSize, windowSize, imgarr, nucmap, covmap, inner_mat, outer_mat)
    nucmap = np.divide(nucmap, covmap)
    
    # Normalize the output image: 
    nucmap = (nucmap * output_stdev) + output_mean

    # Set the name of the output image: 
    pred_img_temp = output_dir + 'out_' + str(j) + '_' + impath 

    print(pred_img_temp)

    # Convert output image to 16-bit type:
    nucmap = nucmap.clip(min=0.0)
    nucmap = nucmap[bord:img_shape[0]+bord,bord:img_shape[1]+bord]
    nucmap_arr = nucmap.astype('uint16')
    # Save the output image:
    tiff = TIFF.open(pred_img_temp, mode='w')
    tiff.write_image(nucmap_arr)
    tiff.close()
    return 

# Set stride to 64 pixels in each direction and window (patch) size.
stepSize = 64
windowSize = (256,256)

# Get the files from the input folder and sort them by name.
impathlist = get_file_list_from_dir(input_dir)
impathlist.sort()

pred_img = ''

for i in range(len(impathlist)):

    print('Processing image: %d' % i)
    
    # Read in and normalize the input image: 
    # Original image: 
    impath = impathlist[i]
    
    im = io.imread(input_dir + impath)
    
    for j in range(im.shape[0]):
    
        img = np.array(im[j])
        img = (img - in_mean)/(in_stdev)
        img_shape = np.array(img.shape)

        # Get size parameters:
        bord = 64
        padding = img_shape%256

        # Create blank image: 
        newImg = np.zeros(img_shape-padding+256*2)

        # Add original input image: 
        newImg[bord:img_shape[0]+bord,bord:img_shape[1]+bord]=img
        img = newImg

        # Process each input image: 
        [h, w] = np.shape(img)
        process_one_image(impath, i, j, img, h, w, pred_img, model, stepSize, windowSize, out_mean, out_stdev, img_shape, bord)

        
    image = np.zeros((im.shape[0], im.shape[1], im.shape[2]), 'uint16')
    for j in range(im.shape[0]):
        pred_img_temp = output_dir + 'out_' + str(j) + '_' + impath 
        image[j] = np.array(io.imread(pred_img_temp))

    tiff_stack_name = output_dir + 'stack_' + str(i) + '_'+ impath 
    imsave(tiff_stack_name, image)
    for j in range(im.shape[0]):
        pred_img_temp = output_dir + 'out_' + str(j) + '_' + impath 
        os.remove(pred_img_temp)
        

elapsed = time.time() - t
print('-------------------------------------------')
print('Total Directory Processing Time: Elapsed time in seconds: %d' % elapsed)
print('-------------------------------------------')






