//
// Created by C. Zhang on 2021/2/4.
//

#ifndef REPAIRCPP_STATE_H
#define REPAIRCPP_STATE_H

# include "action.h"

class state {
public:
    double s{};
    int stage{};

    state() {
        this->s = 0.0;
        this->stage = 0;
    };

    state(double s, int stage);

    state(state const &s);

    std::string to_string();

    static double evaluate();

    double evaluate(action &action);

    std::pair<int, state> apply(const action& ac, double a, double b, int repair_lead_time);
};


#endif //REPAIRCPP_STATE_H
