//
// Created by chuwen on 2021/2/6.
//

#ifndef DUALNEWSVENDOR_DP_H
#define DUALNEWSVENDOR_DP_H

#include <iostream>
#include <fstream>
#include <array>
#include <random>
#include <thread>
#include <future>
#include "Eigen/Dense"
#include "Eigen/Core"
#include "nlohmann/json.hpp"
#include "problem_queue.h"
#include "sol.h"

using json = nlohmann::json;
using array = Eigen::ArrayXd;
using int_array = Eigen::ArrayXi;

double evaluate(state &s, action &ac, double multiplier);

std::vector<double>
run_dp_single(double *lambda, double c, int N, double a, double b, double L, int tau, double s0, bool print, bool truncate);

std::vector<double> run_dp_batch(
        int size,
        double *lambda,
        double *c,
        int N,
        double *a,
        double *b,
        double L,
        int *tau,
        double *s0,
        bool print,
        bool truncate
);

json parse_json(char *fp);

json parse_json(const std::string &fp);

int run_test(char *fp, bool bool_batch_test, bool bool_speed_test);

int run_batch_test(char *fp);
#endif //DUALNEWSVENDOR_DP_H
