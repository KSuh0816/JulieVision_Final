#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH -t 00:15:00
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=ksuh@princeton.edu
#SBATCH --output=argonne_sequence2.out
#SBATCH --mem=100G

module load anaconda3/2023.3
module load cudatoolkit/11.6
module load cudnn/cuda-11.x/8.2.0
source activate KS2-gpu
python process_new_images_1.py
