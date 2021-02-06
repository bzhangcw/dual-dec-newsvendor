/* File: dp.i */
%module dp

%{
#define SWIG_FILE_WITH_INIT

#include "dp.h"

%}

// int fact(int n);
int run_dp_single(
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