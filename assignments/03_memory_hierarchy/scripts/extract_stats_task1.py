#csd4845 Dimitris Asimakopoulos
#script for extracting L1 Miss Rate and IPC from stats.txt files in benchmark directories for task 1

import os
import re
import csv

benchmark_root = "/home/m1tsos/gem5/hy425/benchmark1" #root directory where the folders are located
output_file = "cache_stats.csv" #create a CSV file to store the results

#open the output CSV file for writing
with open(output_file, mode='w', newline='') as csvfile:
    fieldnames = ['Configuration', 'L1_Miss_Rate', 'IPC']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through the benchmark directories and subdirectories
    for root, dirs, files in os.walk(benchmark_root):
        for file in files:
            if file == "stats.txt":
                stats_file_path = os.path.join(root, file)
                config_name = os.path.basename(root) #extract the configuration name from the folder name

                #print(f"Processing: {stats_file_path}")

                l1_miss_rate = None
                ipc = None

                #read the stats file
                with open(stats_file_path, 'r') as f:
                    for line in f:
                        # print(line.strip())

                        #extract L1 Miss Rate and IPC
                        if "system.cpu.dcache.overallMissRate::total" in line:
                            l1_miss_rate = float(line.split()[1])
                            #print(f"L1 Miss Rate found: {l1_miss_rate}")
                        if "system.cpu.ipc" in line:
                            ipc = float(line.split()[1])
                            #print(f"IPC found: {ipc}")

                #if both values are found, write to the CSV
                if l1_miss_rate is not None and ipc is not None:
                    writer.writerow({'Configuration': config_name, 'L1_Miss_Rate': l1_miss_rate, 'IPC': ipc})
                    print(f"Data written for {config_name}: L1_Miss_Rate = {l1_miss_rate}, IPC = {ipc}")
                else:
                    print(f"Data missing for {config_name}.")

print("Extraction completed. Data saved in 'cache_stats.csv'.")
