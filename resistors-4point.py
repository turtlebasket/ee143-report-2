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

    voltage_diff = df["Voltage"].diff().abs()
    threshold = voltage_diff.mean() + 2 * voltage_diff.std()
    transition_points = voltage_diff[voltage_diff > threshold].index
    start_idx = transition_points[0]
    end_idx = transition_points[-1]
    transition_data = df.iloc[start_idx : end_idx + 1]
    slope, _ = polyfit(transition_data["Current"], transition_data["Voltage"], 1)
    resistance = slope

    info = f"Device {device} resistance: {resistance:.2f} Ω"
    print(info)
    with open("calcs/resistors-4point.txt", "a") as f:
        f.write(f"{info}\n")

    plt.figure(figsize=(10, 5))
    plt.plot(df["Current"], df["Voltage"], "-", label="IV Sweep")
    plt.plot(
        transition_data["Current"],
        transition_data["Voltage"],
        "r-",
        label="Transition Region",
        linewidth=2,
    )

    plt.xlabel("Current $I$ [A]")
    plt.ylabel("Voltage $V$ [V]")
    plt.grid(True)
    plt.title(f"4-Point Resistor Measurement - Device {device}")
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"figures/{device.upper()}-4point-resistor-IV.png")
    plt.close()
