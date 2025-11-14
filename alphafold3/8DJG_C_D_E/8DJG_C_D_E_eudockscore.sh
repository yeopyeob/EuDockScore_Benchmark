#!/bin/sh
#SBATCH -J 8DJG_C_D_E
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8DJG_C_D_E/8DJG_C_D_E_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_afscores.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8DJG_C_D_E --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8DJG_C_D_E/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/bakup/alphafold3/8DJG_C_D_E/8DJG_C_D_E_eudockscore_out
