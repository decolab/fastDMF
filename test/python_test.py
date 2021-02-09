import unittest
import fastdmf as dmf
import numpy as np

class TestDMF(unittest.TestCase):

    def test_match(self):
        params = dmf.default_params(sigma=0)

        p = __file__.rstrip('python_test.py')
        rates_deco = np.loadtxt(p + 'rates_deco.csv', delimiter=',')
        bold_deco  = np.loadtxt(p + 'bold_deco.csv', delimiter=',')

        stren = params['C'].sum(axis=1)/2
        params['J'] = params['G']*1.5*stren + 1
        r, b = dmf.run(params, 20000, 'both')

        self.assertTrue(np.allclose(r[:,:2000], rates_deco.T))
        self.assertTrue(np.allclose(b, bold_deco.T))


if __name__ == '__main__':
    unittest.main()

