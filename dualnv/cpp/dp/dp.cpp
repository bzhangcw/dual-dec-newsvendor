#include "dp.h"

/*
 * Universal functions
 *
 * */
double evaluate(state &s, action &ac, double multiplier) {
    return int(ac.is_work == 1) * multiplier;
}


Solution run_dp_single_sol(
        double *lambda,
        double c,
        int N,
        double a,
        double b,
        double L,
        int tau,
        double s0,
        bool print = true,
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

    /* Debug logs
        Eigen::ArrayXd c_arr(N);
        for (int i = 0; i < N; i++) {
            cout << *(c + i) << ",";
            c_arr[i] = c[i];
        }
        cout << endl;
    */

    /*
     * define problem queue
     * which is actually a stack (LIFO)
     * */
    auto queue = problem_queue();

    state s_init = state(s0, 0);
    const string k_init = s_init.to_string();
    state_dict[k_init] = s_init;
    queue.insert(s_init);
    while (!queue.is_empty()) {
        auto kv_pair = queue.get_last();
        string k = kv_pair.first;
        state s = kv_pair.second;
        int n = s.stage;
        // cout << s.to_string() << endl;
        if (s.stage >= N) {
            // which means you reach the last stage
            value_dict[k] = state::evaluate();
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
            for (auto &_ac_val: {0, 1, -1}) {
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
                }
                state_dict[new_state_k] = new_state;
                _tails.push_back(new_tail);
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
            double value = value_dict[tl_s_k] + evaluate(tl.st, tl.ac, lambda[n] * c);
            if (value < min_val) {
                min_val = value;
                best_ac = tl.ac;
                best_tail = tl;
                best_st_k = tl_s_k;
            }
        }
        value_dict[k] = min_val;
        tail_star_dict[k] = best_tail;
        queue.pop();
    }

    Eigen::ArrayXXd output = Eigen::ArrayXXd::Zero(N, 4);
    /*
     * generate the best policy
     *
     */
    string current_k = k_init;
    while (true) {
        state s = state_dict[current_k];
        if (s.stage >= N) break;
        output.col(3)[s.stage] = s.s;
        auto got = tail_star_dict.find(current_k);
        if (got == tail_star_dict.end())
            break;
        current_k = got->second.st.to_string();
        auto is_work = got->second.ac.is_work;
        output.col(0)[s.stage] = (is_work == 1) * lambda[s.stage];
        output.col(1)[s.stage] = float(is_work == -1);
        output.col(2)[s.stage] = float(is_work == 1);

    }
    if (print) {
        cout << "@best value:" << value_dict[k_init] << endl;
        cout << "@best policy: \n"
                "reward repair work lifespan\n"
             << output
             << endl;
    }

    auto solStruct = Solution(output, value_dict[k_init]);
    return solStruct;

}


std::vector<double> run_dp_single(
        double *lambda,
        double c,
        int N,
        double a,
        double b,
        double L,
        int tau,
        double s0,
        bool print = true,
        bool truncate = true // whether we truncate strictly @stage N
) {
    auto sol = run_dp_single_sol(lambda, c, N, a, b, L, tau, s0, print, truncate);
    auto array = get_solutions(sol, N, print);
    return array;
}


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
        bool print = true,
        bool truncate = true // whether we truncate strictly @stage N
) {
    /*
     * auto sol = run_dp_single_sol(c, N, a, b, L, tau, s0, print, truncate);
     * auto array = get_solutions(sol, N, print);
     * return array;
     */
    unsigned int nthreads = size;

    std::vector<std::future<Solution>> futures(nthreads);
    std::vector<Solution> outputs(nthreads);
    for (decltype(futures)::size_type i = 0; i < nthreads; ++i) {
        futures[i] = std::async(
                run_dp_single_sol,
                lambda, c[i], N, a[i], b[i], L, tau[i], s0[i], print, truncate
        );
    }
    for (decltype(futures)::size_type i = 0; i < nthreads; ++i) {
        outputs[i] = futures[i].get();
    }

    auto array = get_solutions(outputs, N);
    return array;
}


json parse_json(char *fp) {
    using namespace std;
    ifstream ifs(fp);
    json _json = json::parse(ifs);
    return _json;
}

json parse_json(const std::string &fp) {
    using namespace std;
    ifstream ifs(fp);
    json _json = json::parse(ifs);
    return _json;
}

int run_test(char *fp, bool bool_batch_test = true, bool bool_speed_test = false) {
    using namespace std;
    time_t start_time;
    time_t end_time;
    time(&start_time);  /* get current time; same as: timer = time(NULL)  */

    /*
     * TEST DATA WITH BENCHMARK RESULTS
     * @date: 2021/02/05
     *
     * */
    if (bool_batch_test) { return run_batch_test(fp); }
    json test = parse_json(fp); // benchmark stored at "src/test/test.json"
    if (!bool_speed_test) cout << test.dump(2) << endl;

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
    if (!bool_speed_test) {
        if (N == 5) {
            double c0[] = {-0.5751079019436339, -0.026884933935354738, -0.7125255181905054, -0.10770288960149066,
                           -0.5392229576522433, -0.23078240408226935, -0.6128866913345116, -0.2954506914149363,
                           -0.48980848777558306, -0.41303183086466067}; // 2.75
            double c1[] = {-0.7127880426437507, -0.5659706571481583, -0.4550456819963197, -0.4958330603215182,
                           -0.4915044667753743, -0.46593208077888737, -0.7663454211766438, -0.2788126396413988,
                           -0.056291269036947034, -0.4476142259600049}; // 2.91
            double c2[] = {-0.09221111835216411, -0.7119915204805928, -0.05008315149821718, -0.060805373703190724,
                           -0.9100117664910027, -0.7912614250104067, -0.25440552456677945, -0.7596541281026525,
                           -0.1311693310130878, -0.1896127093580806}; // 3.17
            double c3[] = {-0.950964750856392, -0.4154944318479806, -0.49231440714337793, -0.6421424832507828,
                           -0.0542522335485478, -0.8453473896111343, -0.07653416889402609, -0.7997331172218721,
                           -0.48645964251958385, -0.44671620871332085}; // 3.60
            double c4[] = {-0.5597228619548954, -0.41248534223116784, -0.9746206013126346, -0.17545187065408596,
                           -0.22512148925156905, -0.3217034035286185, -0.5818429443491299, -0.6022893435405621,
                           -0.89940023010885, -0.6361390464933777}; // 4.01

            __unused auto status0 = run_dp_single(c0, 1,  N, a, b, L, tau, s0);
            __unused auto status1 = run_dp_single(c1, 1,  N, a, b, L, tau, s0);
            __unused auto status2 = run_dp_single(c2, 1, N, a, b, L, tau, s0);
            __unused auto status3 = run_dp_single(c3, 1,  N, a, b, L, tau, s0);
            __unused auto status4 = run_dp_single(c4, 1, N, a, b, L, tau, s0);
            return 1;
        }
        if (N == 20) {
            double c0[] = {-2.43732, -5.08001, -8.83009, -2.70797, -8.94776, -7.93972, -2.58655, -3.96225, -9.25911,
                           -5.37123, -9.23084,
                           -8.02637, -2.56384, -6.17786, -2.06662, -1.6506, -6.34907, -9.173, -4.36922,
                           -6.49543}; // 40.34791
            __unused auto status0 = run_dp_single(c0, 1,  N, a, b, L, tau, s0);
            return 1;
        }
    }
    /*
     * initialize random seed to run test
     * */
    random_device rd;
    mt19937 mt(rd());
    uniform_real_distribution<double> dist(1.0, 10.0);
    double cl[10] = {1.0};
    for (int i = 0; i < 10; i++) {
        double cval[N];
        for (int j = 0; j < N; j++) cval[j] = -dist(mt);
        for (int j = 0; j < N; j++) cout << cval[j] << ",";
        cout << endl;
        run_dp_single(cval, 1.0, N, a, b, L, tau, s0, !bool_speed_test);
    }
    time(&end_time);
    cout << "test finished for "
         << string(fp)
         << " in: "
         << difftime(end_time, start_time)
         << " seconds"
         << endl;
    return 1;
}

int run_batch_test(char *fp) {
    using namespace std;
    time_t start_time;
    time_t end_time;
    time(&start_time);  /* get current time; same as: timer = time(NULL)  */

    /*
     * TEST DATA WITH BENCHMARK RESULTS
     * @date: 2021/02/05
     *
     * */
    json test = parse_json(fp); // benchmark stored at "src/test/test.json"

    int N = test["T"].size();
    int i_N = test["a"].size();

    /*
     * initialize random seed to run test
     * */
    random_device rd;
    mt19937 mt(rd());
    uniform_real_distribution<double> dist(1.0, 10.0);
    double cval[N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) cval[j] = -dist(mt);
//        for (int j = 0; j < N; j++) cout << cval[j] << ",";
//        cout << endl;
    }

    double single_vals[i_N];
    for (int idx = 0; idx < i_N; ++idx) {
        auto a = test["a"][idx].get<double>();
        auto b = test["b"][idx].get<double>();
        auto L = test["L"].get<double>();
        auto tau = test["tau"][idx].get<int>();
        auto s0 = test["s0"][idx].get<double>();
        auto array = run_dp_single(cval, 1.0, N, a, b, L, tau, s0, false, false);
        single_vals[idx] = array.back();
        cout << single_vals[idx] << ",";
    }
    cout << endl;
    auto L = test["L"].get<double>();
    auto a_arr = test["a"].get<vector<double>>();
    auto b_arr = test["b"].get<vector<double>>();
    auto tau_arr = test["tau"].get<vector<int>>();
    auto s0_arr = test["s0"].get<vector<double>>();
    double *cl = new double[i_N];
    std::fill_n(cl, i_N, 1.0);
    auto array_batch = run_dp_batch(i_N, cval, cl, N, a_arr.data(), b_arr.data(), L, tau_arr.data(), s0_arr.data(), false,
                                    false);
    int out_index = 0;
    for (int idx = 0; idx < i_N; ++idx) {
        cout << array_batch[out_index + N * 3] << ",";
    }
    cout << endl;
    return 1;
}