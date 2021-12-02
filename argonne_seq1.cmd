#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH -t 24:00:00
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=ksuh@princeton.edu
#SBATCH --output=argonne_sequence2.out
#SBATCH --mem=100G

module load anaconda3
module load cudnn/cuda-10.1
source activate tf-gpu
python process_images_wo_stats.py
