//
// Created by C. Zhang on 2021/2/7.
//
#include <iostream>
#include <Eigen/Dense>
#include "sol.h"

Solution::Solution(Eigen::ArrayXXd &output, double v) {
    x = output.col(0).data();
    m = output.col(1).data();
    s = output.col(2).data();
    value = v;
    Eigen::ArrayXd compactSol(output.col(0).size() * 3);
    compactSol << output.col(2), output.col(1), output.col(0);
    concat = compactSol.data();
}

double *Solution::get_x() const {
    return this->x;
}

double *Solution::get_m() const {
    return this->m;
}

std::vector<double> get_solutions(Solution &sol, int size, bool verbose=false) {

    auto rtl = std::vector<double>(sol.concat, sol.concat + size * 3);
    rtl.push_back(sol.value);
    if (verbose) {
        for (auto &x: rtl) std::cout << x << ",";
    }
    return rtl;
}