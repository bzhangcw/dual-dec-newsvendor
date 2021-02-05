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

int run_dp_single(
        double *c,
        int N,
        double a,
        double b,
        double L,
        int tau,
        double s0,
        bool truncate = true // whether we truncate strictly @stage N
) {
    /*
     * define containers
     * */
    using namespace std;
    state_map state_dict = state_map();
    action_map action_dict = action_map();
    value_map value_dict = value_map();
    tail_map tail_dict = tail_map();
    best_tail_map tail_star_dict = best_tail_map();
    std::vector<double> c_arr = std::vector<double>(*c);
    for(auto &c_i: c_arr) cout << c_i << ",";
    cout << endl;
    /*
     * define problem queue
     * */
    auto queue = problem_queue();

    state s_init = state(s0, 0);
    string k_init = s_init.to_string();
    state_dict[k_init] = s_init;
    queue.insert(s_init);
    while (!queue.is_empty()) {
        auto kv_pair = queue.get_last();
        string k = kv_pair.first;
        state s = kv_pair.second;
        int n = s.stage;
        cout << s.to_string() << endl;
        if (s.stage >= N) {
            // which means you reach the last stage
            value_dict[k] = state::evaluate();
            action_dict[k] = action_vec();
            queue.pop();
            continue;
        }
        auto _tails = tail_dict[k];
        if (!_tails.empty()) {
            /*
             * tail problems already defined
             * */
        } else {
            /*
             * this gives new tail problems
             * */
            for (auto &_ac_val: {0, 1}) {
                action ac = action(_ac_val);
                auto new_stage_and_tail = s.apply(ac, a, b, tau);
                auto new_state = new_stage_and_tail.second;
                string new_state_k = new_state.to_string();
                if (new_state.s < L) {
                    continue;
                    // which violates the lower bound;
                }
                auto new_tail = tail(new_state, ac);
                auto got = value_dict.find(new_state_k);
                if (got == value_dict.end()) {
                    queue.insert(new_state);
                    state_dict[new_state_k] = new_state;
                    _tails.push_back(new_tail);
                }
            }
            tail_dict[k] = _tails;
            continue;
        }
        /*
         * all tail problems has been solved,
         * do value eval
         * summarize all tail problem
         *
         * */
        double min_val = 1e5;
        action best_ac;
        tail best_tail;
        string best_st_k;

        for (auto &tl : _tails) {
            auto tl_s_k = tl.st.to_string();
            double value = value_dict[tl_s_k] + evaluate(tl.st, tl.ac, c[n]);
            if (value < min_val) {
                min_val = value;
                best_ac = tl.ac;
                best_tail = tl;
                best_st_k = tl_s_k;
            }
        }
        value_dict[k] = min_val;
        /*
         * auto actions = action_vec(action_dict[best_st_k]);
            actions.push_back(best_ac);
            action_dict[k] = actions;
         */
        tail_star_dict[k] = best_tail;
        queue.pop();
    }

    cout << value_dict[k_init] << endl;

    Eigen::ArrayXXd output(N + 1, 2);
    /*
     * generate the best policy
     * */

    string& current_k = k_init;
    while (true) {
        state s = state_dict[current_k];
        output.col(1)[s.stage] = s.s;
        auto got = tail_star_dict.find(current_k);
        if (got == tail_star_dict.end())
            break;
        current_k = got->second.st.to_string();
        auto is_work = got->second.ac.is_work;
        output.col(0)[s.stage] = is_work;
    }
    cout << " action lifespan\n";
    cout << output << endl;
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
    auto tau = test["L"].get<int>();
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
