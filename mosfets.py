import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

mosfet_characteristic_values = {}
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

            if meas_num == "2":
                # I_OFF I_ON
                i_off = df[abs(df["Voltage"]) < 0.1]["Current"].iloc[0] * 1e6
                i_on = df[df["Voltage"] == df["Voltage"].max()]["Current"].iloc[0] * 1e6

                # V_TH (region w/ greatest rate of change)
                di_dv = np.diff(df["Current"]) / np.diff(df["Voltage"])
                max_slope_idx = np.argmax(di_dv)
                # prefer higher of x-coords
                v_th = df["Voltage"].iloc[max_slope_idx + 1]

                # Calculate I_ON/I_OFF ratio
                ion_ioff_ratio = i_on / i_off

                print(f"I_OFF = {i_off:.2f} µA")
                print(f"I_ON = {i_on:.2f} µA")
                print(f"V_TH = {v_th:.2f} V")
                print(f"I_ON/I_OFF = {ion_ioff_ratio:.2f}")

                mosfet_characteristic_values[section] = {
                    "i_off": i_off,
                    "i_on": i_on,
                    "v_th": v_th,
                    "ion_ioff_ratio": ion_ioff_ratio,
                }

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

if mosfet_characteristic_values:
    os.makedirs("calcs", exist_ok=True)
    with open("calcs/mosfets.txt", "w") as f:

        def sort_key(s):
            num = "".join(c for c in s if c.isdigit())
            alpha = "".join(c for c in s if c.isalpha())
            return (int(num), alpha)

        for section in sorted(mosfet_characteristic_values.keys(), key=sort_key):
            f.write(f"\nMOSFET {section}\n")
            f.write(
                f"I_OFF = {mosfet_characteristic_values[section]['i_off']:.2f} µA\n"
            )
            f.write(f"I_ON = {mosfet_characteristic_values[section]['i_on']:.2f} µA\n")
            f.write(f"V_TH = {mosfet_characteristic_values[section]['v_th']:.2f} V\n")
            f.write(
                f"I_ON/I_OFF = {mosfet_characteristic_values[section]['ion_ioff_ratio']:.2f}\n"
            )
