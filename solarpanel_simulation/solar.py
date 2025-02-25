import openmdao.api as om
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # For 3D plotting

# Increase global font size for better readability.
plt.rcParams.update({'font.size': 10})

# -------------------------------
# Simulation Component Definition
# -------------------------------
class SolarPanelSim(om.ExplicitComponent):
    """
    A simulation component for a solar panel array.
    
    This component models the energy output of a solar panel array as a function of:
      - tilt (in radians)
      - orientation (in radians)
      - spacing (in meters)
      - panel_efficiency (dimensionless, e.g., 0.18 for 18% efficiency)
    
    The model uses a combination of Gaussian-like behavior for tilt and orientation,
    a quadratic penalty for deviations in spacing, and a small seasonal factor.
    """
    def setup(self):
        # Inputs: design variables and parameters.
        self.add_input('tilt', val=0.7, units='rad')
        self.add_input('orientation', val=0.0, units='rad')
        self.add_input('spacing', val=10.0, units='m')
        self.add_input('panel_efficiency', val=0.2)
        
        # Output: simulated energy (arbitrary units).
        self.add_output('energy', val=0.0)
        
        # Use finite differences for derivative approximations.
        self.declare_partials('*', '*', method='fd')
    
    def compute(self, inputs, outputs):
        # Retrieve inputs.
        tilt = inputs['tilt']
        orientation = inputs['orientation']
        spacing = inputs['spacing']
        panel_efficiency = inputs['panel_efficiency']
        
        # Define optimum parameters.
        optimum_tilt = 0.7
        optimum_orientation = 0.0
        optimum_spacing = 10.0
        
        # A seasonal factor adds slight periodic variation.
        seasonal_factor = np.sin(tilt + orientation) * 0.1
        
        # Spacing penalty: if panels are too close, the effective energy drops.
        spacing_penalty = 1.0 if spacing >= optimum_spacing else 0.5
        
        # Artificial energy model:
        energy = panel_efficiency * (np.exp(-((tilt - optimum_tilt)**2) -
                                           ((orientation - optimum_orientation)**2) +
                                           seasonal_factor -
                                           0.05 * (spacing - optimum_spacing)**2)) * spacing_penalty
        
        outputs['energy'] = energy

# -------------------------------
# Main Problem Setup and Execution
# -------------------------------
if __name__ == '__main__':
    # Create an OpenMDAO problem instance.
    prob = om.Problem()
    model = prob.model

    # ---- 1. Set Up Independent Variables ----
    ivc = model.add_subsystem('ivc', om.IndepVarComp(), promotes=['*'])
    ivc.add_output('tilt', 0.5, units='rad')
    ivc.add_output('orientation', 0.2, units='rad')
    ivc.add_output('spacing', 12.0, units='m')
    ivc.add_output('panel_efficiency', 0.18)

    # ---- 2. Add the Solar Panel Simulation Component ----
    model.add_subsystem('solar_sim', SolarPanelSim(), 
                        promotes_inputs=['tilt', 'orientation', 'spacing', 'panel_efficiency'])
    
    # ---- 3. Set Up the Objective ----
    model.add_subsystem('obj_comp', om.ExecComp('obj = -energy'))
    model.connect('solar_sim.energy', 'obj_comp.energy')
    model.add_objective('obj_comp.obj')
    
    # ---- 4. Declare Design Variables and Their Bounds ----
    model.add_design_var('tilt', lower=0.0, upper=np.pi/2)
    model.add_design_var('orientation', lower=-np.pi, upper=np.pi)
    model.add_design_var('spacing', lower=5.0, upper=20.0)
    
    # ---- 5. Set Up the Optimization Driver with Recorder ----
    prob.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-6)
    recorder = om.SqliteRecorder("cases.sql")
    prob.driver.add_recorder(recorder)
    prob.driver.recording_options['record_objectives'] = True
    prob.driver.recording_options['record_desvars'] = True
    prob.driver.recording_options['record_constraints'] = True

    # Setup and run the optimization.
    prob.setup()
    prob.run_driver()

    # Output optimized results.
    print("Optimized tilt (rad):", prob.get_val('tilt'))
    print("Optimized orientation (rad):", prob.get_val('orientation'))
    print("Optimized spacing (m):", prob.get_val('spacing'))
    print("Maximum energy (arb. units):", prob.get_val('solar_sim.energy'))
    
    # ---- 6. Visualizations ----

    # 6a. Generate an N2 Diagram of the model architecture.
    
    # 6b. Convergence Plot: Plot the objective value (-energy) versus iteration.
    cr = om.CaseReader("./solar_out/cases.sql")
    driver_case_names = cr.list_cases('driver')
    
    iterations = np.arange(len(driver_case_names))
    objectives = []
    for case_name in driver_case_names:
        case = cr.get_case(case_name)
        obj_dict = case.get_objectives()
        objectives.append(obj_dict.get('obj_comp.obj', np.nan))
    
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, objectives, marker='o', linestyle='-', color='darkblue')
    plt.xlabel('Iteration', fontsize=16)
    plt.ylabel('Objective Value (-Energy)', fontsize=16)
    plt.title('Optimization Convergence', fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("convergence_plot.png")
    print("Convergence plot saved as 'convergence_plot.png'.")
    plt.show()

    # Set fixed values for the design space plots.
    # We use the optimum values as defined in our simulation: 
    fixed_tilt = 0.7
    fixed_orientation = 0.0
    fixed_spacing = 10.0
    fixed_efficiency = 0.18

    # 6c. Design Space Plot: Energy vs. Tilt.
    tilt_vals = np.linspace(0, np.pi/2, 50)
    energy_vs_tilt = []
    
    sim_comp = SolarPanelSim()
    sim_comp.setup()
    for t in tilt_vals:
        inputs = {'tilt': t, 
                  'orientation': fixed_orientation, 
                  'spacing': fixed_spacing, 
                  'panel_efficiency': fixed_efficiency}
        outputs = {}
        sim_comp.compute(inputs, outputs)
        energy_vs_tilt.append(outputs['energy'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(tilt_vals, energy_vs_tilt, '-o', color='darkgreen')
    plt.xlabel('Tilt Angle (radians)', fontsize=16)
    plt.ylabel('Energy Output (arb. units)', fontsize=16)
    plt.title('Energy Output vs. Tilt Angle\n(Orientation=0, Spacing=10 m)', fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("energy_vs_tilt.png")
    print("Energy vs. Tilt plot saved as 'energy_vs_tilt.png'.")
    plt.show()

    # 6d. Design Space Plot: Energy vs. Orientation.
    orientation_vals = np.linspace(-np.pi, np.pi, 50)
    energy_vs_orientation = []
    
    for o in orientation_vals:
        inputs = {'tilt': fixed_tilt, 
                  'orientation': o, 
                  'spacing': fixed_spacing, 
                  'panel_efficiency': fixed_efficiency}
        outputs = {}
        sim_comp.compute(inputs, outputs)
        energy_vs_orientation.append(outputs['energy'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(orientation_vals, energy_vs_orientation, '-o', color='purple')
    plt.xlabel('Orientation (radians)', fontsize=16)
    plt.ylabel('Energy Output (arb. units)', fontsize=16)
    plt.title('Energy Output vs. Orientation\n(Tilt=0.7 rad, Spacing=10 m)', fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("energy_vs_orientation.png")
    print("Energy vs. Orientation plot saved as 'energy_vs_orientation.png'.")
    plt.show()

    # 6e. Design Space Plot: Energy vs. Spacing.
    spacing_vals = np.linspace(5, 20, 50)
    energy_vs_spacing = []
    
    for s in spacing_vals:
        inputs = {'tilt': fixed_tilt, 
                  'orientation': fixed_orientation, 
                  'spacing': s, 
                  'panel_efficiency': fixed_efficiency}
        outputs = {}
        sim_comp.compute(inputs, outputs)
        energy_vs_spacing.append(outputs['energy'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(spacing_vals, energy_vs_spacing, '-o', color='brown')
    plt.xlabel('Spacing (m)', fontsize=16)
    plt.ylabel('Energy Output (arb. units)', fontsize=16)
    plt.title('Energy Output vs. Spacing\n(Tilt=0.7 rad, Orientation=0)', fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("energy_vs_spacing.png")
    print("Energy vs. Spacing plot saved as 'energy_vs_spacing.png'.")
    plt.show()

    # 6f. 3D Surface Plot: Energy vs. Tilt and Orientation.
    tilt_range = np.linspace(0, np.pi/2, 50)
    orientation_range = np.linspace(-np.pi, np.pi, 50)
    TILT, ORIENTATION = np.meshgrid(tilt_range, orientation_range)
    ENERGY = np.zeros_like(TILT)
    
    sim_comp_3d = SolarPanelSim()
    sim_comp_3d.setup()
    
    for i in range(TILT.shape[0]):
        for j in range(TILT.shape[1]):
            inputs = {
                'tilt': TILT[i, j],
                'orientation': ORIENTATION[i, j],
                'spacing': fixed_spacing,
                'panel_efficiency': fixed_efficiency
            }
            outputs = {}
            sim_comp_3d.compute(inputs, outputs)
            ENERGY[i, j] = outputs['energy']
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    surface = ax.plot_surface(TILT, ORIENTATION, ENERGY, cmap='plasma', edgecolor='none', alpha=0.9)
    ax.set_xlabel('Tilt Angle (radians)', fontsize=16)
    ax.set_ylabel('Orientation (radians)', fontsize=16)
    ax.set_zlabel('Energy Output (arb. units)', fontsize=16)
    ax.set_title('3D Energy Surface\nvs. Tilt and Orientation', fontsize=18)
    fig.colorbar(surface, shrink=0.5, aspect=10, pad=0.1, label='Energy Output')
    plt.tight_layout()
    plt.savefig("energy_surface.png")
    print("3D surface plot saved as 'energy_surface.png'.")
    plt.show()
