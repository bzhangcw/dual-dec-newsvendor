#include <iostream>
#include <fstream>
#include <queue>
#include<array>
#include "Eigen/Dense"
#include "Eigen/Core"
#include "nlohmann/json.hpp"
#include "problem_queue.h"

using json = nlohmann::json;
using matrix = Eigen::MatrixXd;
using array = Eigen::ArrayXd;
using int_array = Eigen::ArrayXi;

/*
 * Universal functions
 *
 * */
double evaluate(state &s, action &ac, double multiplier) {
    return ac.is_work * multiplier;
}

int run_dp_single(double *c, int N, double a, double b, double L, double tau, double s0 = 1.0) {

    /*
     * define containers
     * */
    state_map state_dict = state_map();
    action_map action_dict = action_map();
    value_map value_dict = value_map();
    tail_map tail_dict = tail_map();
    /*
     * define problem queue
     * */
    auto queue = problem_queue();

    state s_init = state(s0, 0);
    state_dict[s_init.to_string()] = s_init;
    queue.insert(s_init);
    while (!queue.is_empty()) {
        auto kv_pair = queue.get_last();
        std::string k = kv_pair.first;
        state s = kv_pair.second;
        if (s.stage >= N) {// which means you reach the last stage
            value_dict[k] = s.evaluate();
            action_dict[k] = action_vec();
            queue.pop();
            continue;
        }
        auto _tails = tail_dict[k];
        if (!_tails.empty()) {}
        else {
            // this gives new tail problems
        }
    }
    return 0;
}


int main(int argc, char *argv[]) {
    using namespace std;
    ifstream ifs(argv[1]);
    json test = json::parse(ifs);

    cout << test.dump(2) << endl;

    int N = test["T"].size();
    int idx = 0;
    auto a = test["a"][idx].get<double>();
    auto b = test["b"][idx].get<double>();
    auto L = test["L"].get<double>();
    auto tau = test["L"].get<double>();
    auto cc = test["cc"];
    auto s0 = test["s0"].get<double>();
    double c[N];
    int index = 0;
    for (auto &x: cc) {
        c[index] = x;
        index++;
    }
    int status = run_dp_single(c, N, a, b, L, tau, s0);
    return status;
}
