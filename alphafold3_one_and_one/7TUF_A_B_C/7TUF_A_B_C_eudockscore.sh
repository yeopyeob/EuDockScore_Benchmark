#!/bin/sh
#SBATCH -J 7TUF_A_B_C
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/7TUF_A_B_C/7TUF_A_B_C_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_afscores.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/7TUF_A_B_C --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/7TUF_A_B_C/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/alphafold3_one_and_one/7TUF_A_B_C/7TUF_A_B_C_eudockscore_out
