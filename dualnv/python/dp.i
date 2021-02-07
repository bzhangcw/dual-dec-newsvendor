/* File: dp.i */
%module dp
%include "carrays.i"
%include "std_vector.i"
%include "cpointer.i"

// arrays and vectors
%array_class(double, double_array);
%pointer_functions(double, doubleP);

namespace std
{
    %template(DoubleVector) vector<double>;
}


%{
#define SWIG_FILE_WITH_INIT
#include "dp.h"
#include "sol.h"
%}


std::vector<double> run_dp_single(
        double *c,
        int N,
        double a,
        double b,
        double L,
        int tau,
        double s0,
        bool print,
        bool truncate // whether we truncate strictly @stage N
);
