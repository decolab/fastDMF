/**
 * C++ BoostPython interface to fast DMF simulator to generate BOLD signals.
 * See README.md and DMF.hpp for details.
 *
 * Pedro Mediano, June 2020
 */
#include "../../cpp/DMF.hpp"
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
namespace bp = boost::python;
namespace np = boost::python::numpy;


/**
 * Return pointer to data in a np.ndarray.
 *
 * @param v np.ndarray
 */
double *safeGet(np::ndarray v) {
    return reinterpret_cast<double*>(v.get_data());
}


/**
 * Check whether input ndarray is scalar by checking if it has length 1 in all
 * dimensions.
 *
 * @param v np.ndarray
 */
bool isScalar(np::ndarray v) {
    int const nd = v.get_nd();
    for (int i = 0; i < nd; i++) {
        if (v.shape(i) > 1) {
            return false;
        }
    }
    return true;
}


/**
 * Turn a BoostPython dictionary into a DMF-compatible ParamStruct. The
 * ParamStruct type is defined in DMF.hpp and made to be compatible with
 * BoostPython and Matlab's C Mex interface.
 *
 * @param d BoostPython dict with strings as keys and np.ndarrays as values
 */
ParamStruct struct2map(const bp::dict &d) {

    ParamStruct params;

    bp::list items = d.items();
    for(bp::ssize_t i = 0; i < len(items); ++i) {
        bp::extract<std::string> key(items[i][0]);
        bp::extract<np::ndarray> value(items[i][1]);

        std::string s("isvector_");
        s.append(key);

        if (value.check()) {
            double *p = safeGet(value);
            params[key] = p;
            params[s] = isScalar(value) ? NULL : p;
        } else {
            throw std::invalid_argument("Invalid value in parameter dictionary");
        }
    }

    checkParams(params);

    return params;
}


/**
 * Main BoostPython class to interface with the C++ FastDMF implementation.
 *
 * Exposes only a constructor and a run() method to run simulation and return
 * results.
 */
class DMF : public DMFSimulator {

public:

  DMF(bp::dict d, size_t nb_steps, size_t N, bool return_rate, bool return_bold) :
    DMFSimulator(struct2map(d), nb_steps, N, return_rate, return_bold) {}

  void run(np::ndarray rate_res, np::ndarray bold_res) {
    DMFSimulator::run(safeGet(rate_res), safeGet(bold_res));
  }

};


BOOST_PYTHON_MODULE(_DMF) {
    Py_Initialize();
    np::initialize();

    bp::class_<DMF, boost::noncopyable>("DMF", bp::init<bp::dict, size_t, size_t, bool, bool>())
          .def("run", &DMF::run);

}

