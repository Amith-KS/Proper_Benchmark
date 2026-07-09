import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import platform  # NEW: needed to detect real architecture instead of hardcoding it

# Use relative paths so it works anywhere
df = pd.read_csv("results/combined.csv")
# FILTER: Keep only the keygen data!
df = df[df.operation == "keygen"]
ops = ["keygen"]
libs = ["mlkem-native", "PQClean"]
colors = {"mlkem-native": "#2E86AB", "PQClean": "#E76F51"}

# NEW: detect the real architecture + compiler this script is running under.
# platform.machine() returns things like 'x86_64', 'arm64', 'aarch64' depending on OS.
ARCH = platform.machine()

# --- Chart 1: grouped bar chart of median timing (Keygen Only) ---
fig, ax = plt.subplots(figsize=(5, 5)) # Made slightly narrower
x = np.arange(len(ops))
width = 0.35
for i, lib in enumerate(libs):
    medians = [df[(df.library == lib) & (df.operation == op)].microseconds.median() for op in ops]
    p99s = [df[(df.library == lib) & (df.operation == op)].microseconds.quantile(0.99) for op in ops]
    bars = ax.bar(x + (i - 0.5) * width, medians, width, label=lib, color=colors[lib])
    
    # error bar showing p99 as upper whisker
    errs = [p99 - med for med, p99 in zip(medians, p99s)]
    ax.errorbar(x + (i - 0.5) * width, medians, yerr=[[0]*len(errs), errs],
                fmt='none', ecolor='black', capsize=4, linewidth=1)
    
    for xi, m in zip(x + (i - 0.5) * width, medians):
        ax.text(xi, m + 0.5, f"{m:.1f}", ha='center', va='bottom', fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(["Keygen"])
ax.set_ylabel("Time (microseconds, median, N=5000)")
# CHANGED: title now includes the real detected architecture
ax.set_title(f"ML-KEM-512 Keygen: mlkem-native vs PQClean\n({ARCH} host build)")
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("results/timing_comparison.png", dpi=150)
plt.close()

# --- Chart 2: code size comparison ---
# NOTE: these sizes are still hardcoded, same problem the architecture label had.
# If you rebuild on a different machine/compiler/arch, these numbers go stale
# just like "x86_64" did. Consider replacing with an actual `size` command call
# on your compiled binaries if you want this to self-update too, e.g.:
#   import subprocess
#   out = subprocess.run(["size", "bench_mlkem_native"], capture_output=True, text=True)
#   # parse .text column from out.stdout
sizes = {"mlkem-native": 45299, "PQClean": 56031} 
fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(sizes.keys(), sizes.values(), color=[colors[k] for k in sizes])
for bar, v in zip(bars, sizes.values()):
    ax.text(bar.get_x() + bar.get_width()/2, v + 500, f"{v:,} B", ha='center', fontsize=10)
ax.set_ylabel(".text size (bytes)")
# CHANGED: was hardcoded "O3, gcc, x86_64 host build" — now reflects real arch
ax.set_title(f"Compiled Code Size (.text segment)\nO3, gcc, {ARCH} host build")
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("results/codesize_comparison.png", dpi=150)
plt.close()

# --- Chart 3: distribution box plot (Keygen Only) ---
fig, ax = plt.subplots(figsize=(6, 4.5)) # Reduced to 1 subplot instead of 3
data = [df[df.library == lib].microseconds.values for lib in libs]
bp = ax.boxplot(data, labels=libs, showfliers=False, patch_artist=True)
for patch, lib in zip(bp['boxes'], libs):
    patch.set_facecolor(colors[lib])
    patch.set_alpha(0.7)
ax.set_ylabel("microseconds")
ax.grid(axis='y', linestyle='--', alpha=0.5)
# CHANGED: also stamped with real arch so it's traceable which machine produced it
plt.title(f"Keygen Timing Distribution (N=5000, outliers hidden)\n({ARCH} host build)")
plt.tight_layout()
plt.savefig("results/distribution_boxplots.png", dpi=150)
plt.close()

print(f"Charts saved for Keygen only. Detected architecture: {ARCH}")
print(df.groupby(["library", "operation"]).microseconds.agg(["mean", "median", "std", "min", "max"]))
