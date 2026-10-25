#csd4845 Dimitris Asimakopoulos
#script to extract the Bandwidth and IPC from the stats.txt files of the benchmark folders for task 3

import os
import csv

benchmark_root = "/home/m1tsos/gem5/hy425/benchmark1"


l2_prefetchers = ["StridePrefetcher", "TaggedPrefetcher"]
prefetch_degrees = [1, 2, 3, 4]

output_file = "cache_stats.csv"


with open(output_file, mode='w', newline='') as csvfile:
    fieldnames = ['Configuration', 'DRAM_Bandwidth', 'IPC']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for l2_pref in l2_prefetchers:
        for pref_deg in prefetch_degrees:

            folder_name = f"m5out_TASK:3_cacheline_sz:128_l1d_assoc:8_l2_sz:2048kB_l2_assoc:16_rp_type:LRURP_l2_clus:mostly_excl_l2_pref:{l2_pref}_pref_deg:{pref_deg}"
            folder_path = os.path.join(benchmark_root, folder_name)
            stats_file_path = os.path.join(folder_path, "stats.txt")


            #print(f"Processing folder: {folder_name}")

            dram_bw = None
            ipc = None
            if os.path.exists(stats_file_path):
                with open(stats_file_path, 'r') as f:
                    for line in f:
                        if "system.mem_ctrl.dram.bwTotal::total" in line:
                            dram_bw = float(line.split()[1])
                            #print(f"DRAM Bandwidth found: {dram_bw}")

                        if "system.cpu.ipc" in line:
                            ipc = float(line.split()[1])
                            #print(f"IPC found: {ipc}")

                if dram_bw is not None and ipc is not None:
                    writer.writerow({
                        'Configuration': folder_name,
                        'DRAM_Bandwidth': dram_bw,
                        'IPC': ipc
                    })
                    print(f"Data written for {folder_name}: DRAM_Bandwidth = {dram_bw}, IPC = {ipc}")
                else:
                    print(f"Data missing for {folder_name}.")
            else:
                print(f"stats.txt not found in folder: {folder_name}")

print("Extraction completed. Data saved in 'cache_stats.csv'.")
