# Save this script as, e.g., hvac_simulation.py and run it with Python

# Step 1: Write a simple Modelica model to a file (HVACModel.mo)
modelica_code = r'''
model HVACModel
  "A simple HVAC model with a dynamic indoor temperature and sinusoidal outdoor temperature."
  
  // Parameters for the HVAC system and building
  parameter Real T_set = 22 "Desired indoor temperature (°C)";
  parameter Real U = 0.5 "Heat transfer coefficient";
  parameter Real C = 500 "Thermal capacity";
  parameter Real Q = 0 "HVAC input power (W) - set to 0 for open-loop simulation";
  
  // Variables
  Real T(start=T_set) "Indoor temperature (°C)";
  Real T_out "Outdoor temperature (°C)";
  
equation
  // Define outdoor temperature as a sinusoidal function of time (time in minutes)
  T_out = 15 + 5*sin(2*3.14*time/1440);
  
  // Thermal dynamics: rate of change of indoor temperature
  der(T) = (Q + U*(T_out - T)) / C;
end HVACModel;
'''

# Write the model code to a file
with open("HVACModel.mo", "w") as f:
    f.write(modelica_code)
print("Modelica model written to HVACModel.mo")

# Step 2: Use OMPython to load, instantiate, and simulate the model
from OMPython import OMCSessionZMQ
import os

# Create an OpenModelica session
omc = OMCSessionZMQ()

# Load the Modelica file
load_result = omc.sendExpression('loadFile("HVACModel.mo")')
print("Load result:", load_result)

# Optionally, check for errors
error_str = omc.sendExpression("getErrorString()")
if error_str:
    print("Modelica load error:", error_str)

# Instantiate the model
inst_result = omc.sendExpression("instantiateModel(HVACModel)")
print("Instantiation result:", inst_result)

# Simulate the model
# Here we simulate for 1440 minutes with 1440 intervals (1-minute resolution)
sim_result = omc.sendExpression('simulate(HVACModel, stopTime=1440, numberOfIntervals=1440, method="dassl", outputFormat="csv")')
print("Simulation result summary:", sim_result)

# print error
error_str = omc.sendExpression("getErrorString()")
print("Error string:", error_str)

# Step 3: Read simulation results from the result file
# The result file is typically a CSV file produced by OpenModelica
simulation_file = sim_result.get("resultFile")
if not simulation_file or not os.path.exists(simulation_file):
    raise FileNotFoundError("Simulation result file not found: " + str(simulation_file))

print('result file:', simulation_file)

# Convert the simulation data (a dictionary) to a Pandas DataFrame for easy plotting
import pandas as pd
df = pd.read_csv(simulation_file)

# Display a preview of the data
print(df.head())

# Step 4: Visualize the simulation results
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(df["time"], df["T"], label="Indoor Temperature")
plt.plot(df["time"], df["T_out"], label="Outdoor Temperature", linestyle="--")
plt.axhline(22, color="gray", linestyle=":", label="Setpoint (22°C)")
plt.xlabel("Time (minutes)")
plt.ylabel("Temperature (°C)")
plt.title("HVAC Simulation: Indoor vs Outdoor Temperature")
plt.legend()
plt.grid(True)
plt.show()
