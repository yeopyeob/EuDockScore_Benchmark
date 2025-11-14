#!/bin/sh
#SBATCH -J 7YRU_H_L_A
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/7YRU_H_L_A/7YRU_H_L_A_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_afscores.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/7YRU_H_L_A --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/7YRU_H_L_A/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/7YRU_H_L_A/7YRU_H_L_A_eudockscore_out
