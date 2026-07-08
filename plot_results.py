import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("/home/claude/bench/results/combined.csv")

ops = ["keygen", "encaps", "decaps"]
libs = ["mlkem-native", "PQClean"]
colors = {"mlkem-native": "#2E86AB", "PQClean": "#E76F51"}

# --- Chart 1: grouped bar chart of median timing per operation ---
fig, ax = plt.subplots(figsize=(8, 5))
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
ax.set_xticklabels([o.capitalize() for o in ops])
ax.set_ylabel("Time (microseconds, median, N=5000)")
ax.set_title("ML-KEM-512: mlkem-native vs PQClean\n(median time per operation; whiskers = p99)")
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("/home/claude/bench/results/timing_comparison.png", dpi=150)
plt.close()

# --- Chart 2: code size comparison ---
fig, ax = plt.subplots(figsize=(6, 4))
sizes = {"mlkem-native": 45299, "PQClean": 56031}  # .text bytes from `size`
bars = ax.bar(sizes.keys(), sizes.values(), color=[colors[k] for k in sizes])
for bar, v in zip(bars, sizes.values()):
    ax.text(bar.get_x() + bar.get_width()/2, v + 500, f"{v:,} B", ha='center', fontsize=10)
ax.set_ylabel(".text size (bytes)")
ax.set_title("Compiled Code Size (.text segment)\nO3, gcc, x86_64 host build")
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("/home/claude/bench/results/codesize_comparison.png", dpi=150)
plt.close()

# --- Chart 3: distribution box plot per operation ---
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=False)
for ax, op in zip(axes, ops):
    data = [df[(df.library == lib) & (df.operation == op)].microseconds.values for lib in libs]
    bp = ax.boxplot(data, labels=libs, showfliers=False, patch_artist=True)
    for patch, lib in zip(bp['boxes'], libs):
        patch.set_facecolor(colors[lib])
        patch.set_alpha(0.7)
    ax.set_title(op.capitalize())
    ax.set_ylabel("microseconds")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.suptitle("Timing Distribution per Operation (N=5000, outliers hidden)")
plt.tight_layout()
plt.savefig("/home/claude/bench/results/distribution_boxplots.png", dpi=150)
plt.close()

print("Charts saved.")
print(df.groupby(["library", "operation"]).microseconds.agg(["mean", "median", "std", "min", "max"]))
