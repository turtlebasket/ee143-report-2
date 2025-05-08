import pandas as pd
import matplotlib.pyplot as plt
import re

filename = "data/CVSweep4284_a [(8) _5 LIGHT OFF_; 4_8_2025 12_15_56 PM].csv"

data_values = []
with open(filename, "r") as f:
    for line in f:
        if line.startswith("DataValue"):
            parts = line.strip().split(",")
            if len(parts) == 4:
                try:
                    voltage = float(parts[1])
                    capacitance = float(parts[2])
                    data_values.append([voltage, capacitance])
                except (ValueError, IndexError):
                    continue

if data_values:
    df = pd.DataFrame(data_values, columns=["Voltage", "Capacitance"])

    plt.figure(figsize=(10, 5))
    plt.plot(df["Voltage"], df["Capacitance"], "-")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Capacitance (F)")
    plt.grid(True)
    plt.title("CV Characteristic - Device 5 (Light off)")
    plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    plt.tight_layout()

    plt.savefig("figures/5-cap-light-off.png")
    plt.close()
