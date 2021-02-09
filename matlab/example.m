%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Example usage of DMF fMRI simulator.
%
% Pedro Mediano, Apr 2020
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Fetch default parameters
params = DefaultParams();

% Run simulation
nb_steps = 20000;
b = DMF(params, nb_steps);

