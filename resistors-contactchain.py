# devices 2C, 2D

import pandas as pd
import matplotlib.pyplot as plt
from numpy import polyfit

filenames = [
    "data/I_V Sweep [(8) 2C light off; 4_1_2025 10_40_23 AM].csv",
    "data/I_V Sweep [(10) 2D light off; 4_1_2025 10_41_37 AM].csv",
]

device_resistances = {}

for file in filenames:
    device = "2C" if "2C" in file else "2D"

    data_values = []
    with open(file, "r") as f:
        for line in f:
            if line.startswith("DataValue"):
                parts = line.strip().split(",")
                if len(parts) == 3:
                    try:
                        voltage = float(parts[1])
                        current = float(parts[2])
                        data_values.append([voltage, current])
                    except (ValueError, IndexError):
                        continue

    df = pd.DataFrame(data_values, columns=["Voltage", "Current"])

    # R = V/I = 1/(I/V)
    slope, _ = polyfit(df["Voltage"], df["Current"], 1)
    resistance = 1 / slope
    device_resistances[device] = resistance

    plt.figure(figsize=(10, 5))
    plt.plot(df["Voltage"], df["Current"], "-", label=f"IV Sweep")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.grid(True)
    plt.title(f"Contact Chain Measurement - Device {device}")
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"figures/{device.upper()}-contactchain-IV.png")
    plt.close()

with open("calcs/resistors-contactchain.txt", "w") as f:
    for device, resistance in device_resistances.items():
        f.write(f"Device {device}: {resistance:.2f} Ω\n")
