import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import interp1d
import imageio
import os

# -------------------------------
# Problem Setup
# -------------------------------
g = 9.81         # gravitational acceleration (m/s^2)
L = 1.0          # horizontal distance (m)
H = 2.0          # vertical drop (m); y increases from near 0 to H
N = 100          # number of discretization points

# Discretize x from 0 to L
x = np.linspace(0, L, N)
dx = L / (N - 1)

# Set boundary conditions for y (vertical drop)
y_start = 1e-3   # small value >0 to avoid division by zero
y_end = H

# Initial guess: a linear interpolation between y_start and y_end
y_initial = np.linspace(y_start, y_end, N)
# We optimize only the interior points (indices 1 to N-2)
y_interior_initial = y_initial[1:-1]

# -------------------------------
# Total Time Functional
# -------------------------------
def total_time(y_interior):
    """
    Compute the total travel time T for the brachistochrone curve
    using a trapezoidal rule.
    """
    y_full = np.concatenate(([y_start], y_interior, [y_end]))
    T = 0.0
    for i in range(N - 1):
        dydx = (y_full[i+1] - y_full[i]) / dx
        y_mid = (y_full[i+1] + y_full[i]) / 2.0
        # Avoid division by zero:
        if y_mid < 1e-6:
            y_mid = 1e-6
        integrand = np.sqrt(1 + dydx**2) / np.sqrt(2 * g * y_mid)
        T += integrand * dx
    return T

# -------------------------------
# Constraints and Bounds
# -------------------------------
# Ensure the interior y-values are non-decreasing
constraints = []
for i in range(len(y_interior_initial) - 1):
    constraints.append({'type': 'ineq', 'fun': lambda y, i=i: y[i+1] - y[i]})
# Also ensure first interior value >= y_start and last <= y_end
constraints.append({'type': 'ineq', 'fun': lambda y: y[0] - y_start})
constraints.append({'type': 'ineq', 'fun': lambda y: y_end - y[-1]})
# Bounds for each interior value
bounds = [(y_start, y_end) for _ in range(len(y_interior_initial))]

# -------------------------------
# Optimize with SLSQP and Capture Intermediate States
# -------------------------------
intermediate_solutions = []  # list to store intermediate full y curves

def callback_func(x_curr):
    # x_curr: current interior y-values; reconstruct the full y curve
    y_full = np.concatenate(([y_start], x_curr, [y_end]))
    intermediate_solutions.append(y_full.copy())

result = minimize(total_time, y_interior_initial, method='SLSQP',
                  bounds=bounds, constraints=constraints,
                  callback=callback_func, options={'maxiter': 1000})
y_interior_opt = result.x
y_opt = np.concatenate(([y_start], y_interior_opt, [y_end]))
print("Optimized total travel time: {:.4f} seconds".format(total_time(y_interior_opt)))

# -------------------------------
# Create a Ball Sliding Animation Along the Optimized Curve
# -------------------------------
# Compute cumulative time along the optimized curve
times = [0]
for i in range(len(x) - 1):
    dydx = (y_opt[i+1] - y_opt[i]) / dx
    y_mid = (y_opt[i+1] + y_opt[i]) / 2.0
    if y_mid < 1e-6:
        y_mid = 1e-6
    dt = dx * np.sqrt(1 + dydx**2) / np.sqrt(2 * g * y_mid)
    times.append(times[-1] + dt)
times = np.array(times)
total_time_opt = times[-1]

# Create interpolation functions to map time to position along the curve.
f_x = interp1d(times, x, kind='linear')
f_y = interp1d(times, y_opt, kind='linear')

# Set up animation parameters: number of frames and sampled times
num_frames = 100
t_samples = np.linspace(0, total_time_opt, num_frames)

frames = []
temp_frame_file = "temp_ball_frame.png"

for t in t_samples:
    x_ball = f_x(t)
    y_ball = f_y(t)
    
    plt.figure(figsize=(6, 4))
    # Plot the optimized brachistochrone as a reference curve
    plt.plot(x, y_opt, 'b-', label='Optimized Brachistochrone')
    # Plot the moving ball at the current position
    plt.plot(x_ball, y_ball, 'ro', markersize=8, label='Sliding Ball')
    plt.xlabel('Horizontal Distance (m)')
    plt.ylabel('Vertical Drop (m)')
    plt.title('Ball Sliding Along the Brachistochrone')
    plt.legend()
    plt.gca().invert_yaxis()  # Invert y-axis: deeper drop is lower on the plot
    plt.tight_layout()
    plt.savefig(temp_frame_file)
    plt.close()
    frames.append(imageio.imread(temp_frame_file))

os.remove(temp_frame_file)
output_gif_ball = "ball_sliding_brachistochrone.gif"
imageio.mimsave(output_gif_ball, frames, duration=0.05)
print("Ball sliding GIF saved to", output_gif_ball)
