#!/bin/sh
#SBATCH -J 6Z3Q
#SBATCH -p gpu-super.q
#SBATCH --nodelist=nova[004,005,008,009,010]
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c 8
#SBATCH -o /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock/unbound/6Z3Q/6Z3Q_eudockscore.log.q
python /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/scripts/run_eudockscore_data_ab.py --root_dir /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock/unbound/6Z3Q --csv_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock/unbound/6Z3Q/eudockscore_input.csv --file_name /home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/zdock/unbound/6Z3Q/6Z3Q_eudockscore_out
