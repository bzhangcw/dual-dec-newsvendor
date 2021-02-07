//
// Created by C. Zhang on 2021/2/7.
//

#ifndef DUALNEWSVENDOR_SOL_H
#define DUALNEWSVENDOR_SOL_H
#include <vector>
class Solution {
public:

    double *x;
    double *s;
    double *m;
    double value;
    double *concat;

    Solution(){
        x = nullptr;
        s = nullptr;
        m = nullptr;
        value = 0.0;
        concat = nullptr;
    }

    Solution(Eigen::ArrayXXd &array, double v);

    ~Solution() = default;
    double * get_x() const;
    double * get_s() const;
    double * get_m() const;

};

std::vector<double> get_solutions(Solution &s, int size, bool print);
#endif //DUALNEWSVENDOR_SOL_H
