import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

data_files = glob.glob("data/MOSFET*.csv")


def plot_iv_curves(voltage, current, threshold=0.1):
    traces_v = []
    traces_i = []
    curr_v_trace = []
    curr_i_trace = []

    # first trace
    curr_v_trace.append(voltage[0])
    curr_i_trace.append(current[0])

    # NOTE: detect resets by looking for voltage near zero after being higher,
    # then save & start new trace
    for i in range(1, len(voltage)):
        if abs(voltage[i]) < threshold and abs(voltage[i - 1]) > threshold:
            traces_v.append(curr_v_trace)
            traces_i.append(curr_i_trace)
            curr_v_trace = []
            curr_i_trace = []

        curr_v_trace.append(voltage[i])
        curr_i_trace.append(current[i])

    # final trace
    traces_v.append(curr_v_trace)
    traces_i.append(curr_i_trace)

    # plot each trace separately
    plt.figure()
    for idx, (v, i) in enumerate(zip(traces_v, traces_i)):
        plt.plot(v, i, "-", label=f"Sweep {idx+1}")

    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.grid(True)
    plt.title(f"Device ({section}) - Measurement {meas_num}")
    plt.legend()
    plt.tight_layout()


for file in data_files:
    print(f"\nProcessing: {file}")

    filename = os.path.basename(file)
    match = re.search(r"MOSFET MEAS(\d+) \[.*_(\d+[A-Z]?).*MEAS(\d+)", filename)
    if match:
        device_num = match.group(1)
        section = match.group(2)
        meas_num = match.group(3)
        plot_filename = f"figures/{section}-meas{meas_num}.png"
        plot_title = f"Device ({section}) - Measurement {meas_num}"
    else:
        print(f"Could not parse filename pattern: {filename}")
        continue

    data_values = []
    try:
        with open(file, "r") as f:
            for line in f:
                if line.startswith("DataValue"):
                    parts = line.strip().split(",")
                    if len(parts) != 3:
                        continue
                    try:
                        x = float(parts[1])
                        y = float(parts[2])
                        data_values.append([x, y])
                    except (ValueError, IndexError):
                        continue

        if data_values:
            df = pd.DataFrame(data_values, columns=["Voltage", "Current"])

            plot_iv_curves(df["Voltage"].values, df["Current"].values)
            plt.savefig(plot_filename)
            plt.close()
            print(f"Saved plot as: {plot_filename}")

        else:
            print(f"No valid data found in {file}")

    except Exception as e:
        print(f"Error processing {file}: {str(e)}")
