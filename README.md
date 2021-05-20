Fast simulator of the Dynamic Mean Field model of brain dynamics
================================================================

This C++ software implements the Dynamic Mean Field (DMF) model of brain
dynamics, originally published by Gustavo Deco (UPF) and collaborators (see
references below).

This implementation offers four main advantages over the original Matlab
implementation by Deco *et al*:

1. It is written in C++, which already makes it faster (integration of DMF
   equations is about 3x faster than in Matlab).

2. The Balloon-Windkessel model of BOLD response is run in parallel with the
   DMF model itself, adding a further ~2x speedup when BOLD signals are
   requested.

3. If only BOLD time series are requested, the DMF simulator runs on a circular
   buffer, which radically reduces memory consumption.

4. It offers APIs for both Octave/Matlab and Python.

This software is distributed with a "modified" 3-clause BSD licence, and
contains an unmodified copy of the [Eigen](http://eigen.tuxfamily.org/) library
under the MPL licence.

Pedro Mediano, Andrea Luppi, and Fernando Rosas, Feb 2021

[[_TOC_]]


## Simulation parameters

The model equations are parameterised by certain properties of the brain's
neural, synaptic, and hemodynamic processes. The list of default parameters is
provided by the functions `DefaultParams.m` (in Octave/Matlab) and
`default_params` (in Python), and the full list is provided in the table below:

| Parameter name |  Default  | Description |
| -------------- | --------- | ----------- |
| `C`            | See below | Structural (i.e. anatomical) connecivity matrix |
| `receptors`    | 0\*       | Receptor density (AU) |
| `dt`           | 0.1       | DMF integration step (ms) |
| `taon`         | 100       | NMDA characteristic time (ms) |
| `taog`         | 10        | GABA characteristic time (ms) |
| `gamma`        | 0.641     | Kinetic parameter of excitation |
| `sigma`        | 0.01      | Noise standard deviation (nA) |
| `JN`           | 0.15      | Excitatory synaptic coupling (nA) |
| `I0`           | 0.382     | Effective external input (nA) |
| `Jexte`        | 1         | External-to-excitatory coupling |
| `Jexti`        | 0.7       | External-to-inhibitory coupling |
| `w`            | 1.4       | Local excitatory recurrence |
| `g_e`          | 0.16      | Excitatory conductance |
| `Ie`           | 0.403     | Excitatory threshold for nonlinearity |
| `ce`           | 310       | Excitatory nonlinear shape parameter |
| `g_i`          | 0.087     | Inhibitory conductance |
| `Ii`           | 0.288     | Inhibitory threshold for nonlinearity |
| `ci`           | 615       | Inhibitory nonlinear shape parameter |
| `wgaine`       | 0         | Excitatory neuromodulatory gain |
| `wgaini`       | 0         | Inhibitory neuromodulatory gain |
| `G`            | 2         | Global coupling parameter |
| `J`            | See below | Feedback inhibitory control parameter |
| `TR`           | 2         | BOLD signal sampling frequency (s) |
| `dtt`          | 0.001     | BW integration step (s) |
| `batch_size`   | 5000      | Parallel computation batch size |

Parameter `C` is the structural connectivity matrix of the model, typically
obtained via diffusion tensor imaging (DTI). The default matrix provided was
obtained from the 1200-subject release of the [HCP
dataset](http://www.humanconnectome.org) using a 100-node Schaeffer
parcellation.

Parameter `J` represents the strength of the feedback inhibitory control at
each node. In Deco *et al.* [(2018)](www.doi.org/10.1016/j.cub.2018.07.083) it
is optimised to keep all firing rates at approximately 3 Hz. The default uses a
heuristic `J = 0.75*G*S + 1`, where `S` is the node strength in the structural
connectivity matrix (Herzog _et al_.,
[2020](https://www.doi.org/10.1038/s41598-020-74060-6); in prep.).

Parameters marked with an asterisk (\*) may be provided as a scalar or as an
array of length equal to the number of nodes in `C`, in which case they are
taken to represent a value for each ROI.

For further information on these parameters, see the [references](#references).


## Usage in Octave/Matlab

To compile the code from Matlab, make sure you are in the `FastDMF/matlab`
folder, and run:

```octave
mex COPTIMFLAGS="-O3" DMF.cpp
```

If for any reason you do not want the DMF and BOLD integrators to run in
parallel (because of system constraints or as a speed test), you can use the
`NO_PARALLEL` compiler flag:

```octave
mex COPTIMFLAGS="-O3" DMF.cpp -DNO_PARALLEL
```

In Octave, you may have to remove the `COPTIMFLAGS` option, and instead use the
`CXXFLAGS` environment variable. See `help mkoctfile` for details.

Once compiled, you may just add the `matlab` folder to the path and use as
follows:

```octave
params = DefaultParams();
nb_steps = 20000;
bold = DMF(params, nb_steps);
```

Above, `nb_steps` is the number of DMF (not BOLD) steps to integrate, and
`params` is a `struct` with all relevant parameters (see `DefaultParams.m`).
The resulting matrix, `bold` is of size `NxT`, with N variables and T
timesteps.

One can also request firing rates and/or BOLD signals through an optional third
argument to `DMF` (*note*: number of output arguments has to match, otherwise
the code will throw an error):

```octave
rate = DMF(params, nb_steps, 'rate');
bold = DMF(params, nb_steps, 'bold');
[rate, bold] = DMF(params, nb_steps, 'both');
```


## Usage in Python

The Python API is implemented as a C++ extension, and depends on the
[Boost.Python](https://github.com/boostorg/python) library. To install it in
Debian-based OSs, run

```bash
apt-get update
apt-get install libboost-python-dev libboost-numpy-dev
```

For installation in other OSs, please refer to the Boost installation
instructions.

Compilation and installation is handled via `setuptools`, by running e.g.

```bash
python setup.py install
```

Once installed, the library can be imported and used in a similar way to the
Octave/Matlab interface:

```python
import fastdmf as dmf
params = dmf.default_params()
nb_steps = 20000
bold = dmf.run(params, nb_steps)
```


## Implementation notes and possible improvements

* The BOLD integrator operates fully component-wise, suggesting that it could
  be further parallelised into array chunks. However, at the moment the
  simulation is compute-bound by the DMF equations (and not the BW), meaning
  that such a parallelisation may not help much (if at all).

* There are a few points where I think the code might be further optimised for
  a possible extra speedup:

    - Explore the aliasing, in-place operations, and matrix-vector product inside
      the the for-loop in `DMFSimulator::run`.
  
    - Parallelising excitatory and inhibitory computations in the same loop.
  
    - Same considerations for the BW computations in `BOLDIntegrator::compute`.

  Unfortunately, these computations would have pretty short turnaround times,
  so they would ned proper consumer-producer designs (instead of simply
  spawning new threads all the time).


## References

* Luppi, A., _et al_. (2021). _Paths to oblivion: Common neural mechanisms of
  anaesthesia and disorders of consciousness_. BioRxiv. DOI:
  [10.1101/2021.02.14.431140](https://doi.org/10.1101/2021.02.14.431140)

* Deco, G., _et al_. (2018). _Whole-brain multimodal neuroimaging model using
  serotonin receptor maps explains non-linear functional effects of LSD_. Curr.
  Biol. 1–10, DOI:
  [10.1016/j.cub.2018.07.083](https://www.doi.org/10.1016/j.cub.2018.07.083)

* Herzog, R., Mediano, P., Rosas, F., Carhart-Harris, R., Sanz Perl, Y.,
  Tagliazucchi, E. & Cofre, R. (2020). _A mechanistic model of the neural
  entropy increase elicited by psychedelic drugs_. Sci. Rep. 10, 17725, DOI:
  [10.1038/s41598-020-74060-6](https://www.doi.org/10.1038/s41598-020-74060-6)

* Deco, G., Hagmann, P., Romani, G. L., Mantini, D. & Corbetta, M. (2014). _How
  local excitation-inhibition ratio impacts the whole brain dynamics_. J.
  Neurosci. 34, 7886–7898, DOI:
  [10.1523/JNEUROSCI.5068-13.2014](https://www.doi.org/10.1523/JNEUROSCI.5068-13.2014)

