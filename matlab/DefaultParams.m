function [ params ] = DefaultParams(varargin)
%%DEFAULTPARAMS Default parameter settings for DMF simulation
%
%   P = DEFAULTPARAMS() yields a struct with default values for all necessary
%   parameters for the DMF model. The default structural connectivity is the
%   DTI fiber consensus matrix obtained from the HCP dataset, using a
%   Schaeffer-100 parcellation.
%
%   P = DEFAULTPARAMS('key', 'value', ...) adds (or replaces) field 'key' in
%   P with given value.
%
% Pedro Mediano, Feb 2021

params = [];

% Connectivity matrix
if any(strcmp(varargin, 'C'))
  C = [];

else
  try
    p = strrep(mfilename('fullpath'), 'DefaultParams', '');
    C = dlmread([p, '../data/DTI_fiber_consensus_HCP.csv'], ',');
    C = C/max(C(:));
  catch
    error('No connectivity matrix provided, and default matrix not found.');
  end

end


% DMF parameters
params.C         = C;
params.receptors = 0;
params.dt        = 0.1;   % ms
params.taon      = 100;   % NMDA tau ms
params.taog      = 10;    % GABA tau ms
params.gamma     = 0.641; % Kinetic Parameter of Excitation
params.sigma     = 0.01;  % Noise SD nA
params.JN        = 0.15;  % excitatory synaptic coupling nA
params.I0        = 0.382; % effective external input nA
params.Jexte     = 1.;    % external->E coupling
params.Jexti     = 0.7;   % external->I coupling
params.w         = 1.4;   % local excitatory recurrence
params.g_e       = 0.16;  % excitatory conductance
params.Ie        = 125.;  % excitatory threshold for nonlineariy
params.ce        = 310.;  % excitatory non linear shape parameter
params.g_i       = 0.087; % inhibitory conductance
params.Ii        = 177.;  % inhibitory threshold for nonlineariy
params.ci        = 615.;  % inhibitory non linear shape parameter
params.wgaine    = 0;     % neuromodulatory gain
params.wgaini    = 0;     % neuromodulatory gain
params.G         = 2;     % Global Coupling Parameter

% Balloon-Windkessel parameters (from firing rates to BOLD signal)
params.subsamp      = 2;     % number of seconds to sample bold signal
params.dtt          = 0.001; % seconds

% Parallel computation parameters
params.batch_size = 5000;

% Add/replace remaining parameters
for i=1:2:length(varargin)
  params.(varargin{i}) = varargin{i+1};
end

% If feedback inhibitory control not provided, use heuristic
if ~any(strcmp(varargin, 'J'))
  params.J = 1.5*params.G*sum(params.C, 1)' + 1;
end

end

