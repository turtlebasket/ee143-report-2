import pandas as pd
import matplotlib.pyplot as plt
import re

filenames = [
    "data/CVSweep4284_a [(4) _3 LIGHT OFF_; 4_8_2025 12_00_08 PM].csv",
    "data/CVSweep4284_a [(5) _4 LIGHT ON_; 4_8_2025 12_05_20 PM].csv",
    "data/CVSweep4284_a [(6) _4 LIGHT OFF_; 4_8_2025 12_07_43 PM].csv",
]

for file in filenames:
    if "_3" in file:
        device = "3"
        light = "off"
    elif "_4" in file:
        device = "4"
        match = re.search(r"LIGHT (ON|OFF)", file)
        light = match.group(1).lower()

    data_values = []
    with open(file, "r") as f:
        for line in f:
            if line.startswith("DataValue"):
                parts = line.strip().split(",")
                if len(parts) == 4:  # Voltage, Capacitance, Dispersion
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
        plt.title(f"CV Characteristic - Device {device} (Light {light})")
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        plt.tight_layout()

        plt.savefig(f"figures/{device}-cap-light-{light}.png")
        plt.close()
