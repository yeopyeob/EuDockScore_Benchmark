#!/bin/sh
#SBATCH -J 8PE1_D_#_B
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/8PE1_D_#_B/8PE1_D_#_B_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_afscores.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/8PE1_D_#_B --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/8PE1_D_#_B/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/8PE1_D_#_B/8PE1_D_#_B_eudockscore_out
