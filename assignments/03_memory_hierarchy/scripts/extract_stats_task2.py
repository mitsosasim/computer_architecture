#csd4845 Dimitris Asimakopoulos
#script to extract the Global Miss Rate and IPC from the stats.txt files of the benchmark folders for task 2

import os
import csv

benchmark_root = "/home/m1tsos/gem5/hy425/benchmark1"

#define the parameters and their values
l2_sizes = ["512kB", "1024kB", "2048kB"]
l2_assocs = [4, 8, 16]
replacement_policies = ["FIFORP", "RandomRP", "LRURP"]
l2_clustering = ["mostly_excl", "mostly_incl"]


output_file = "cache_stats.csv"


with open(output_file, mode='w', newline='') as csvfile:
    fieldnames = ['Configuration', 'L1_Miss_Rate', 'IPC']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    #iterate through all combinations of parameters
    for l2_size in l2_sizes:
        for l2_assoc in l2_assocs:
            for rp_type in replacement_policies:
                for l2_clus in l2_clustering:

                    #generate the folder name based on the parameter combination
                    folder_name = f"m5out_TASK:2_cacheline_sz:128_l1d_assoc:8_l2_sz:{l2_size}_l2_assoc:{l2_assoc}_rp_type:{rp_type}_l2_clus:{l2_clus}"
                    folder_path = os.path.join(benchmark_root, folder_name)
                    stats_file_path = os.path.join(folder_path, "stats.txt")

                    #print(f"Processing folder: {folder_name}")

                    l1_miss_rate = None
                    ipc = None

                    if os.path.exists(stats_file_path):
                        with open(stats_file_path, 'r') as f:
                            for line in f:
                                # Extract Miss Rate and IPC using string matching
                                if "system.cpu.dcache.overallMissRate::total" in line:
                                    l1_miss_rate = float(line.split()[1])
                                    #print(f"Miss Rate found: {l1_miss_rate}")

                                if "system.cpu.ipc" in line:
                                    ipc = float(line.split()[1])
                                    #print(f"IPC found: {ipc}")

                        if l1_miss_rate is not None and ipc is not None:
                            writer.writerow({
                                'Configuration': folder_name,
                                'L1_Miss_Rate': l1_miss_rate,
                                'IPC': ipc
                            })
                            print(f"Data written for {folder_name}: L1_Miss_Rate = {l1_miss_rate}, IPC = {ipc}")
                        else:
                            print(f"Data missing for {folder_name}.")
                    else:
                        print(f"stats.txt not found in folder: {folder_name}")

print("Extraction completed. Data saved in 'cache_stats.csv'.")
