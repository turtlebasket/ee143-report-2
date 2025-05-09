# devices 2A, 2B

from numpy import polyfit
import pandas as pd
import matplotlib.pyplot as plt

filenames = [
    "data/I_V Sweep [(6) _2A light off_; 4_1_2025 10_26_44 AM].csv",
    "data/I_V Sweep [(4) _2B light off_; 4_1_2025 10_13_51 AM].csv",
]

for file in filenames:
    device = "2A" if "2A" in file else "2B"

    data_values = []
    with open(file, "r") as f:
        for line in f:
            if line.startswith("DataValue"):
                parts = line.strip().split(",")
                if len(parts) == 3:
                    try:
                        current = float(parts[1])
                        voltage = float(parts[2])
                        data_values.append([current, voltage])
                    except (ValueError, IndexError):
                        continue

    df = pd.DataFrame(data_values, columns=["Current", "Voltage"])

    # R = V/I = 1/(I/V)
    slope, _ = polyfit(df["Voltage"], df["Current"], 1)
    resistance = 1 / slope

    plt.figure(figsize=(10, 5))
    plt.plot(df["Current"], df["Voltage"], "-", label=f"IV Sweep")
    plt.xlabel("Current $I$ [A]")
    plt.ylabel("Voltage $V$ [V]")
    plt.grid(True)
    plt.title(f"4-Point Resistor Measurement - Device {device}")
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"figures/{device.upper()}-4point-resistor-IV.png")
    plt.close()
