
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
