#csd4845 Dimitrios Asimakopoulos
#python script that i used to create the bar graphs for all the tasks. here task 1 can be seen


import matplotlib.pyplot as plt
import numpy as np


block_sizes = ['32', '64', '128']
associativities = ['direct-mapped', '2-way', '4-way', '8-way']
average_ipc = [
    # Block Size 32
    [1.0046512, 1.0152756, 1.0156108, 1.015978],
    # Block Size 64
    [1.2230946, 1.2381476, 1.2385066, 1.2391044],
    # Block Size 128
    [1.3773172, 1.4001932, 1.4015454, 1.4013366]
]

# Plot configuration
x = np.arange(len(block_sizes))  # X-axis positions for block sizes
width = 0.2  # Width of each bar
colors = plt.cm.viridis(np.linspace(0, 1, len(associativities)))  # Color map

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 6))

# Plot bars for each associativity
for i, assoc in enumerate(associativities):
    offsets = x + (i - 1.5) * width
    ax.bar(offsets,
           [avg[i] for avg in average_ipc],
           width,
           label=assoc,
           color=colors[i])

# Add labels and title
ax.set_xlabel('Block Size (bytes)', fontsize=12)
ax.set_ylabel('Average IPC', fontsize=12)
ax.set_title('Average IPC by Cache Configuration', fontsize=14, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(block_sizes)
ax.legend(title='Associativity', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
