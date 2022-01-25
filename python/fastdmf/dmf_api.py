"""
Dynamic Mean Field model

Run simulation of the Dynamic Mean Field model of brain dynamics.

Pedro Mediano, Jun 2020
"""
import _DMF
import numpy as np

__all__ = ['default_params', 'run']

def _format_dict(d):
    """
    Makes sure that every value in the dictionary is a np.array
    
    Parameters
    ----------
    d : dict
        Parameter dictionary with strings as keys.

    Returns
    -------
    q : dict
        Parameter dictionary with strings as keys and np.ndarrays as values.
    """
    q = {}
    for k in d:
        if isinstance(d[k], np.ndarray):
            if not d[k].shape:
                q[k] = d[k].reshape(1).astype(float)
            else:
                q[k] = d[k].astype(float)
        elif isinstance(d[k], (tuple, list)):
            q[k] = np.array(d[k], dtype=float)
        elif np.isscalar(d[k]):
            q[k] = np.array([d[k]], dtype=float)
        else:
            raise ValueError("Parameter %s cannot be cast as float np.array"%s)
    return q


def default_params(**kwargs):
    """
    Default parameters for DMF simulation.

    Parameters
    ----------
    kwargs
        Name-value pairs to add to or replace in the dictionary.

    Returns
    -------
    params: dict
    """

    if 'C' not in kwargs:
        C = np.loadtxt(__file__.rstrip('dmf_api.py') + 'DTI_fiber_consensus_HCP.csv', delimiter=',')
        C = C/C.max()
    else:
        C = []


    # DMF parameters
    params              = {}
    params['C']         = C        # structural connectivity
    params['receptors'] = 0        # receptor density
    params['dt']        = 0.1      # ms
    params['taon']      = 100      # NMDA tau ms
    params['taog']      = 10       # GABA tau ms
    params['gamma']     = 0.641    # Kinetic Parameter of Excitation
    params['sigma']     = 0.01     # Noise SD nA
    params['JN']        = 0.15     # excitatory synaptic coupling nA
    params['I0']        = 0.382    # effective external input nA
    params['Jexte']     = 1.       # external->E coupling
    params['Jexti']     = 0.7      # external->I coupling
    params['w']         = 1.4      # local excitatory recurrence
    params['de']        = 0.16     # excitatory non linear shape parameter
    params['Ie']        = 125/310  # excitatory threshold for nonlinearity
    params['g_e']       = 310.     # excitatory conductance
    params['di']        = 0.087    # inhibitory non linear shape parameter
    params['Ii']        = 177/615  # inhibitory threshold for nonlinearity
    params['g_i']       = 615.     # inhibitory conductance
    params['wgaine']    = 0        # neuromodulatory gain
    params['wgaini']    = 0        # neuromodulatory gain
    params['G']         = 2        # Global Coupling Parameter

    # Balloon-Windkessel parameters (from firing rates to BOLD signal)
    params['TR']  = 2     # number of seconds to sample bold signal
    params['dtt'] = 0.001 # BW integration step, in seconds

    # Parallel computation parameters
    params['batch_size'] = 5000

    # Add/replace remaining parameters
    for k, v in kwargs.items():
        params[k] = v

    # If feedback inhibitory control not provided, use heuristic
    if 'J' not in kwargs:
        params['J'] = 0.75*params['G']*params['C'].sum(axis=0).squeeze() + 1

    return params


def run(params, nb_steps, desired_out='bold'):
    """
    Run the DMF model and return simulated brain activity. Size and number of
    output arguments depends on desired_out.

    Parameters
    ----------
    params : dict
        Parameter dictionary (see default_params()).

    nb_steps : int
        Number of integration steps to compute. Final size of the simulated
        time series depends on selected dt and TR.

    desired_out : {'rate', 'bold' 'both'}, optional
        Type of output to return from the simulation: either firing rate only,
        BOLD only, or both. If'both', output is a (r,b) tuple with two numpy
        arrays. If 'bold', memory consumption is substantially reduced.

    Returns
    -------
    out : tuple or np.ndarray
        Simulated activity of the DMF model. Can be either firing rates, BOLD
        activity, or a tuple with both (see desired_out above).
    """

    if desired_out == 'bold':
        return_rate, return_bold = False, True
    elif desired_out == 'rate':
        return_rate, return_bold = True, False
    elif desired_out == 'both':
        return_rate, return_bold = True, True
    else:
        raise ValueError("desired_out must be one of 'bold', 'rate', or 'both'.")

    # Pre-allocate memory for results
    N = params['C'].shape[0]
    nb_steps_bold = round(nb_steps*params['dtt']/params['TR'])
    if return_rate:
        nb_steps_rate = nb_steps
    else:
        nb_steps_rate = 2*params['batch_size']

    rate_res = np.zeros((N, nb_steps_rate), dtype=float, order='F')
    bold_res = np.zeros((N, nb_steps_bold), dtype=float, order='F')


    # Run simulation
    sim = _DMF.DMF(_format_dict(params), nb_steps, N, return_rate, return_bold)
    sim.run(rate_res, bold_res)


    # Return results
    if desired_out == 'bold':
        out = bold_res
    elif desired_out == 'rate':
        out = rate_res
    elif desired_out == 'both':
        out = (rate_res, bold_res)

    return out

