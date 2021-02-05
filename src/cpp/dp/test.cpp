//
// Created by C. Zhang on 2021/2/4.
//

#include <iostream>
#include <queue>
#include <unordered_map>

#include "Eigen/Dense"
#include "nlohmann/json.hpp"

#include "problem_queue.h"

using Eigen::MatrixXd;
using namespace std;

int main(int argc, char *argv[]) {

    state s0 = state(0.0, 0);
    action ac = action(1);
    tail tl = tail(s0, ac);
    state s1 = state(s0);
    s1.stage = 1;
    s1.s = 2.0;
    tail tl1 = tail(s1, ac);
    cout << s0.to_string() << endl;
    cout << s1.to_string() << endl;
    // test action apply
    auto a1 = s1.apply(action(1), 0.4, 0.8, 2);
    cout << a1.second.to_string() << endl;
    auto a2 = s1.apply(action(0), 0.4, 0.8, 2);
    cout << a2.second.to_string() << endl;
    cout << tl.key << endl;
    problem_queue queue = problem_queue();
    action_map action_dict = action_map();
    action_dict["11"] = action_vec();
    auto acc = action_dict["12"];
    cout << acc.size() << endl;
    acc.push_back(ac);
    cout << action_dict["12"].size() << endl;
    cout << acc.size() << endl;
    return 0;
}