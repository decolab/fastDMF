from setuptools import setup, Extension

ext = Extension('_DMF',
                libraries = ['boost_python3', 'boost_numpy3'],
                sources   = ['fastdmf/DMF.cpp'])

setup(name              = 'fastdmf',
      version          = '0.1',
      description      = 'Fast Dynamic Mean Field simulator of neural dynamics',
      author           = 'Pedro A.M. Mediano',
      author_email     = 'pam83@cam.ac.uk',
      url              = 'https://gitlab.com/concog/fastdmf',
      long_description = open('../README.md').read(),
      package_data     = {'fastdmf': ['DTI_fiber_consensus_HCP.csv']},
      install_requires = ['numpy'],
      ext_modules      = [ext],
      packages         = ['fastdmf'])

