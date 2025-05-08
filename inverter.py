# Device 14

import pandas as pd
import matplotlib.pyplot as plt

filename = "data/MOSFET MEAS2 [(9) _14_; 4_8_2025 11_37_24 AM].csv"


def plot_inverter_curves(voltage, output, threshold=0.1):
    traces_v = []
    traces_out = []
    curr_v_trace = []
    curr_out_trace = []

    curr_v_trace.append(voltage[0])
    curr_out_trace.append(output[0])

    for i in range(1, len(voltage)):
        if abs(voltage[i] + 5) < threshold:  # detect reset to -5V
            if curr_v_trace:  # save current trace if it exists
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
        # Get approximate vdd from max output voltage
        vdd = max(out)
        plt.plot(v, out, "-", label=f"VDD ≈ {vdd:.1f}V")

    plt.xlabel("Input Voltage (V)")
    plt.ylabel("Output Voltage (V)")
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
