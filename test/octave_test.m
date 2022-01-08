%*********************************************************
%
% Unit tests of C++ FastDMF code and its mex interface.
%
% Pedro Mediano, Feb 2021
%
%*********************************************************
p = strrep(mfilename('fullpath'), 'octave_test', '');
if exist([p, '../matlab'], 'dir')
  addpath([p, '../matlab']);
end
tol = 1e-8;

%% Compare against original DMF code by Deco et al
rates_deco = dlmread([p, 'rates_deco.csv'], ',');
bold_deco  = dlmread([p, 'bold_deco.csv'], ',');

params = DefaultParams('sigma', 0);
stren = sum(params.C)./2;
params.J = params.G*1.5*stren + 1;
[r, b] = DMF(params, 20000, 'both');

assert(mean(mean(abs(b - bold_deco'))) < tol);
assert(mean(mean(abs(r(:,1:2000) - rates_deco'))) < tol);


%% Compare single-output with double-output simulations
params = DefaultParams('sigma', 0);
nb_steps = 4000;
[r, b] = DMF(params, nb_steps, 'both');
b_only = DMF(params, nb_steps, 'bold');
r_only = DMF(params, nb_steps, 'rate');

assert(mean(mean(abs(r - r_only))) < tol);
assert(mean(mean(abs(b - b_only))) < tol);


%% Test PRNG seed
params = DefaultParams('seed', 42);
r1 = DMF(params, 100, 'rate');
r2 = DMF(params, 100, 'rate');
params.seed = 21;
r3 = DMF(params, 100, 'rate');

assert(sum(abs(r1(:) - r2(:))) < tol);
assert(sum(abs(r1(:) - r3(:))) > tol);


%% Test nargout errors thrown
error_thrown = false;
try
  [a, b] = DMF(DefaultParams(), 2000, 'bold');
catch
  error_thrown = true;
end
assert(error_thrown);

error_thrown = false;
try
  a = DMF(DefaultParams(), 2000, 'both');
catch
  error_thrown = true;
end
assert(error_thrown);


%% Test empty arrays throw error, but do not core-dump
params = DefaultParams('Jexte', zeros([0,10]));
error_thrown = false;
try
  r = DMF(params, 2000, 'rate');
catch
  error_thrown = true;
end
assert(error_thrown);


%% Test G has no effect in an uncoupled network
params = DefaultParams('C', zeros(2), 'sigma', 0);
r1 = DMF(params, 100, 'rate');
params.G = 0;
r2 = DMF(params, 100, 'rate');

assert(sum(abs(r1(:) - r2(:))) < tol);


%% Test scalar-vector conversion does not alter output
params = DefaultParams('sigma', 0);
nb_steps = 4000;
[r, b] = DMF(params, nb_steps, 'both');
params.Jexte = params.Jexte*ones([size(params.C, 1), 1]);
params.Jexti = params.Jexti*ones([size(params.C, 1), 1]);
[r_vec, b_vec] = DMF(params, nb_steps, 'both');

assert(mean(mean(abs(r - r_vec))) < tol);
assert(mean(mean(abs(b - b_vec))) < tol);


%% Test excitatory external current increases firing rate
params = DefaultParams('C', eye(2), 'Jexte', [1; 5]);
nb_steps = 4000;
r = DMF(params, nb_steps, 'rate');
avg_r = mean(r, 2);

assert(avg_r(2) > avg_r(1));


%% Test region-specific receptor gains
for s={'wgaine', 'wgaini'}
  params = DefaultParams('C', eye(2), 'receptors', 1, s{1}, 1, 'sigma', 0);
  nb_steps = 4000;
  [r, b] = DMF(params, nb_steps, 'both');
  params.(s{1}) = [1; 2];
  [r2, b2] = DMF(params, nb_steps, 'both');

  assert(mean(abs(r(1,:) - r2(1,:))) < tol);
  assert(mean(abs(b(1,:) - b2(1,:))) < tol);
  assert(mean(abs(r(2,:) - r2(2,:))) > tol);
  assert(mean(abs(b(2,:) - b2(2,:))) > tol);
end

