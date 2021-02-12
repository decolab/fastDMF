%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Example usage of DMF fMRI simulator.
%
% Pedro Mediano, Apr 2020
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Fetch default parameters
params = DefaultParams();

% Run simulation for a given nb of steps (milliseconds)
nb_steps = 100000;
BOLD = DMF(params, nb_steps);

% Minimal "post-processing": band-pass filter and remove the starting and
% trailing ends of the simulation to avoid transient and filtering artefacts
[B, A] = butter(2, [0.01, 0.1]*2*params.TR);
BOLD = filter(B, A, BOLD')';

trans = 5;
BOLD = BOLD(:, 1+trans:end-trans);

