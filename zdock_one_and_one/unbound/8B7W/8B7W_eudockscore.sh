#!/bin/sh
#SBATCH -J 8B7W
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock_one_and_one/unbound/8B7W/8B7W_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_ab.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock_one_and_one/unbound/8B7W --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock_one_and_one/unbound/8B7W/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock_one_and_one/unbound/8B7W/8B7W_eudockscore_out
