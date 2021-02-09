"""
Example usage of DMF fMRI simulator.

Pedro Mediano, June 2020
"""
import fastdmf as dmf

# Fetch default parameters
params = dmf.default_params()

# Run simulation
nb_steps = 20000;
b = DMF.run(params, nb_steps);

