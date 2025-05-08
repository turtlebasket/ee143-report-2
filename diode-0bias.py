import pandas as pd
import matplotlib.pyplot as plt

data_values = []
with open("data/I_V Sweep [(26) 7 diode 0bias; 4_1_2025 11_13_52 AM].csv", "r") as f:
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

plt.figure()
plt.plot(df["Voltage"], df["Current"], "-", label="Sweep 1")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (A)")
plt.grid(True)
plt.title("Diode (Device 7): 0V Bias")
plt.legend()
plt.tight_layout()

plt.savefig("figures/7-diode-IV-0bias.png")
plt.close()
