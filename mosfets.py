import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

data_files = glob.glob("data/MOSFET*.csv")

# for labels - ordered in secondary "sweep" step direction
meas1_gate_voltages = [0, 1, 2, 3, 4, 5]
meas2_bias_voltages = [0, -1, -2]


def plot_iv_curves(voltage, current, plot_title, threshold=0.1, log_scale=False):
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
        # (select based on measurement number)
        if meas_num == "1":
            label = f"$V_G$ = {meas1_gate_voltages[idx]}V"
            xlabel = "Drain Voltage $V_D$ [V]"
            ylabel = "Drain Current $I_D$ [A]"
        else:
            label = f"$V_B$ = {meas2_bias_voltages[idx]}V"
            xlabel = "Gate Voltage $V_G$ [V]"
            ylabel = "Drain Current $I_D$ [A]"
            if log_scale:
                plt.yscale("log")
        plt.plot(v, i, "-", label=label)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.title(plot_title + (" (log scale)" if log_scale else ""))
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
        plot_title = f"MOSFET {section} - Measurement {meas_num}"
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

            plot_iv_curves(df["Voltage"].values, df["Current"].values, plot_title)
            plt.savefig(plot_filename)
            plt.close()
            print(f"Saved plot as: {plot_filename}")

            if meas_num == "2":
                plot_iv_curves(
                    df["Voltage"].values,
                    df["Current"].values,
                    plot_title,
                    log_scale=True,
                )
                log_filename = plot_filename.replace(".png", "-logscale.png")
                plt.savefig(log_filename)
                plt.close()
                print(f"Saved log scale plot as: {log_filename}")

        else:
            print(f"No valid data found in {file}")

    except Exception as e:
        print(f"Error processing {file}: {str(e)}")
