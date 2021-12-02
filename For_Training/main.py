
# This is the FRM script to do it all:
# Splits and processes data for training; trains the model; produces predictions on the test set. 

# Set your parameters here:

# Path to raw input/output TIFF files: 
input_dir = '/scratch/gpfs/ksuh/Leicainput/'
output_dir = '/scratch/gpfs/ksuh/Leicaoutput/'

# Path where the scripts can save output:
working_dir = '/scratch/gpfs/ksuh/LeicaWeight081721/'

# Your name for the saved weights file: 
weights_file = 'Leica_4X_weights.h5'

# Imports:
from source import frm_data_split, frm_test_train_split, frm_get_data_stats, frm_train, frm_test

frm_data_split.do_split(input_dir, output_dir, working_dir)
frm_test_train_split.do_test_train_split(working_dir)
X_train, Y_train = frm_get_data_stats.do_get_data_stats(working_dir)
frm_train.do_train(working_dir, weights_file, X_train, Y_train)
frm_test.do_test(working_dir, weights_file)
