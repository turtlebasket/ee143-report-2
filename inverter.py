# Device 14

import pandas as pd
import matplotlib.pyplot as plt

filename = "data/MOSFET MEAS2 [(9) _14_; 4_8_2025 11_37_24 AM].csv"

drain_voltages = [5, 10, 15]


def plot_inverter_curves(voltage, output, threshold=2.0):
    traces_v = []
    traces_out = []
    curr_v_trace = []
    curr_out_trace = []

    curr_v_trace.append(voltage[0])
    curr_out_trace.append(output[0])

    for i in range(1, len(voltage)):
        # Detect when voltage jumps backwards significantly
        if voltage[i] < voltage[i - 1] - threshold:
            if curr_v_trace:  # save current trace if it exists
                # DEBUG
                print(
                    f"split @ index {i}, voltage jump: {voltage[i-1]} -> {voltage[i]}"
                )
                traces_v.append(curr_v_trace)
                traces_out.append(curr_out_trace)
                curr_v_trace = []
                curr_out_trace = []

        curr_v_trace.append(voltage[i])
        curr_out_trace.append(output[i])

    if curr_v_trace:
        traces_v.append(curr_v_trace)
        traces_out.append(curr_out_trace)

    plt.figure(figsize=(10, 5))
    for idx, (v, out) in enumerate(zip(traces_v, traces_out)):
        label = f"$V_D$ = {drain_voltages[idx]}V"
        plt.plot(v, out, "-", label=label)

    plt.xlabel("Input Voltage $V$ [V]")
    plt.ylabel("Output Voltage $V$ [V]")
    plt.grid(True)
    plt.title("Inverter Transfer Characteristic - Device 14")
    plt.legend()
    plt.tight_layout()


data_values = []
with open(filename, "r") as f:
    for line in f:
        if line.startswith("DataValue"):
            parts = line.strip().split(",")
            if len(parts) == 3:
                try:
                    vin = float(parts[1])
                    vout = float(parts[2])
                    data_values.append([vin, vout])
                except (ValueError, IndexError):
                    continue

if data_values:
    df = pd.DataFrame(data_values, columns=["Input", "Output"])
    plot_inverter_curves(df["Input"].values, df["Output"].values)
    plt.savefig("figures/14-inverter-IV.png")
    plt.close()
