# ev_simulation.py

# Step 1: Write the Modelica model code to a file (EVSimulation.mo)
modelica_code = r'''
model ElectricMotor
  parameter Real maxTorque = 300 "Maximum torque (Nm)";
  parameter Real speedNominal = 3000 "Nominal speed (rpm)";
  Real speed "Motor speed (rpm)";
  Real torque "Motor torque (Nm)";
equation
  // Linear decrease of torque with increasing speed
  torque = maxTorque * (1 - speed/speedNominal);
end ElectricMotor;

model Battery
  parameter Real voltageNominal = 400 "Nominal voltage (V)";
  parameter Real internalResistance = 0.01 "Internal resistance (ohm)";
  Real current "Battery current (A)";
  Real voltage "Battery voltage (V)";
equation
  // Voltage drops as current increases
  voltage = voltageNominal - current * internalResistance;
end Battery;

model BatteryThermal
  parameter Real heatCapacity = 500 "Heat capacity (J/K)";
  parameter Real thermalResistance = 0.5 "Thermal resistance (K/W)";
  parameter Real ambientTemperature = 25 "Ambient temperature (°C)";
  Real temperature(start=ambientTemperature) "Battery temperature (°C)";
  Real heatGeneration "Heat generated (W)";
equation
  // Energy balance: C*dT/dt = heat generated - cooling losses
  heatCapacity * der(temperature) = heatGeneration - (temperature - ambientTemperature)/thermalResistance;
end BatteryThermal;

model EVSimulation
  // Define a local constant for pi
  constant Real pi = 3.141592653589793 "Pi constant";
  
  // Instantiate components
  ElectricMotor motor;
  Battery battery;
  BatteryThermal batteryThermal;
  
  // Control parameters: Now a time-varying speed
  parameter Real baseSpeed = 1500 "Base motor speed (rpm)";
  parameter Real amplitude = 500 "Speed variation amplitude (rpm)";
  parameter Real frequency = 0.005 "Speed variation frequency";
  parameter Real currentGain = 0.05 "Gain to convert motor torque to battery current";
  
  // 'time' is provided by the simulation environment (Modelica's built-in variable)
equation
  // Define a time-varying desired motor speed using the local constant for pi
  motor.speed = baseSpeed + amplitude * sin(2 * pi * frequency * time);
  
  // Calculate battery current based on the motor torque load
  battery.current = abs(motor.torque) * currentGain;
  
  // Compute battery heat generation (Joule heating)
  batteryThermal.heatGeneration = battery.current^2 * battery.internalResistance;
end EVSimulation;
'''

with open("EVSimulation.mo", "w") as f:
    f.write(modelica_code)
print("Modelica model written to EVSimulation.mo")

# Step 2: Load, instantiate, and simulate the Modelica model using OMPython
from OMPython import OMCSessionZMQ
import os

# Create an OpenModelica session
omc = OMCSessionZMQ()

# Load the Modelica file
load_result = omc.sendExpression('loadFile("EVSimulation.mo")')
print("Load result:", load_result)

# Check for any load errors
error_str = omc.sendExpression("getErrorString()")
if error_str:
    print("Modelica load error:", error_str)

# Instantiate the model
inst_result = omc.sendExpression("instantiateModel(EVSimulation)")
print("Instantiation result:", inst_result)

# Simulate the model for 1000 seconds with 1000 intervals (1-second resolution)
sim_result = omc.sendExpression('simulate(EVSimulation, stopTime=1000, numberOfIntervals=1000, method="dassl", outputFormat="csv")')
print("Simulation result summary:", sim_result)

error_str = omc.sendExpression("getErrorString()")
print("Error string:", error_str)

# Step 3: Read simulation results from the CSV result file
simulation_file = sim_result.get("resultFile")
if not simulation_file or not os.path.exists(simulation_file):
    raise FileNotFoundError("Simulation result file not found: " + str(simulation_file))

print("Simulation result file:", simulation_file)

import pandas as pd
df = pd.read_csv(simulation_file)
print("Data preview:")
print(df.head())

# Step 4.1: Create a 3D scatter plot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Necessary for 3D plotting

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 3D scatter: X-axis -> time, Y-axis -> battery voltage, Z-axis -> battery temperature
# color -> battery current
scatter = ax.scatter(
    df["time"],
    df["battery.voltage"],
    df["batteryThermal.temperature"],
    c=df["battery.current"],
    cmap='viridis',
    marker='o'
)

ax.set_xlabel('Time (s)')
ax.set_ylabel('Battery Voltage (V)')
ax.set_zlabel('Battery Temperature (°C)')
ax.set_title("3D Scatter: Time vs Voltage vs Temperature (Colored by Battery Current)")
cbar = plt.colorbar(scatter, pad=0.1)
cbar.set_label('Battery Current (A)')

# Step 4.2: Create an Animated 2D Plot
import matplotlib.animation as animation

fig2, ax2 = plt.subplots(figsize=(10, 8))

line2, = ax2.plot([], [], 'r-', label='Battery Temperature (°C)')
line3, = ax2.plot([], [], 'g-', label='Battery Current (A)')

ax2.set_xlim(df["time"].min(), df["time"].max())
# Determine a suitable range for the y-axis based on all three variables
y_min = min(df["batteryThermal.temperature"].min(), df["battery.current"].min())
y_max = max(df["batteryThermal.temperature"].max(), df["battery.current"].max())
ax2.set_ylim(y_min, y_max)

ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Value')
ax2.set_title("Animated 2D Plot: Temperature, and Current over Time")
ax2.legend()
ax2.grid(True)

def init():
    """Initialize empty data for all three lines."""
    line2.set_data([], [])
    line3.set_data([], [])
    return line2, line3

def animate(i):
    """Update each line up to the ith data point."""
    line2.set_data(df["time"][:i], df["batteryThermal.temperature"][:i])
    line3.set_data(df["time"][:i], df["battery.current"][:i])
    return line2, line3

# Create the animation
ani = animation.FuncAnimation(
    fig2, 
    animate, 
    frames=len(df), 
    init_func=init, 
    interval=50,  # milliseconds between frames
    blit=True
)

plt.show()
ani.save("animation.gif", writer="ffmpeg")