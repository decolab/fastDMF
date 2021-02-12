"""
Example usage of DMF fMRI simulator.

Pedro Mediano, June 2020
"""
import fastdmf as dmf
import numpy as np
from scipy.signal import butter, lfilter

# Fetch default parameters
params = dmf.default_params()

# Run simulation for a given nb of steps (milliseconds)
nb_steps = 100000;
BOLD = dmf.run(params, nb_steps);

# Minimal "post-processing": band-pass filter and remove the starting and
# trailing ends of the simulation to avoid transient and filtering artefacts
b, a = butter(2, np.array([0.01, 0.1])*2*params['TR'], btype='band')
BOLD = lfilter(b, a, BOLD)

trans = 5;
BOLD = BOLD[:,trans:-trans]

