"""
Example usage of DMF fMRI simulator.

Pedro Mediano, June 2020
"""
import fastdmf as dmf
import numpy as np
from scipy import signal
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.io as sio

# Fetch default parameters
params = dmf.default_params()

# Run simulation for a given nb of steps (milliseconds)
nb_steps = 10000
BOLD = np.array([dmf.run(params, nb_steps)])

# Minimal "post-processing": band-pass filter and remove the starting and
# trailing ends of the simulation to avoid transient and filtering artefacts
#b, a = butter(2, np.array([0.01, 0.1])*2*params['TR'], btype='band')
#BOLD = lfilter(b, a, BOLD)
#
#trans = 5;
#BOLD = BOLD[:,trans:-trans]

BOLD_out = np.array([BOLD])
print(BOLD_out.shape)
print(BOLD_out)

#plt.figure(1)
#plt.plot(BOLD[0, 0, 0:], label = 'reg.A')
#plt.plot(BOLD[0, 1, 0:], label = 'reg.B')
#plt.plot(BOLD[0, 2, 0:], label = 'reg.C')
#plt.xlabel("Time (ms)")
#plt.ylabel("Population firing rate")
#plt.title("Population firing rate")
#plt.legend(loc="upper right")
#plt.grid()
#plt.show()

mat_contents = sio.loadmat("/Users/corneliasheeran/Desktop/BOLD_data/Schaefer100_BOLD_HCP.mat")
BOLD_compare = mat_contents['BOLD_timeseries_HCP']
#print(BOLD_compare.shape)
newbold = BOLD_compare[0, :]
nn = newbold[0]
print(nn.shape)

#mat_corr = signal.correlate(BOLD_out, BOLD_compare, mode='full', method='auto')
