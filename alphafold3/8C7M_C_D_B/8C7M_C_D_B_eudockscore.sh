#!/bin/sh
#SBATCH -J 8C7M_C_D_B
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8C7M_C_D_B/8C7M_C_D_B_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_afscores.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8C7M_C_D_B --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8C7M_C_D_B/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8C7M_C_D_B/8C7M_C_D_B_eudockscore_out
