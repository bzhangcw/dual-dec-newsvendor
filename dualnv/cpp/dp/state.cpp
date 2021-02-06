//
// Created by C. Zhang on 2021/2/4.
//
#include <string>
#include "state.h"

state::state(double s, int stage) {
    this->s = s;
    this->stage = stage;
}

state::state(const state &s) {
    *this = s;
}

std::string state::to_string() const {
    return std::to_string(this->stage) + "," + std::to_string(this->s);
}

bool operator==(const state &lhs, const state &rhs) {
    return lhs.s == rhs.s && lhs.stage == rhs.stage;
}

double state::evaluate() {
    return 0;
}

std::pair<int, state> state::apply(const action& ac, double a, double b, int repair_lead_time = 2) {
    int lead_time = ac.is_work == - 1 ? repair_lead_time : 1;
    state s1 = *this;
    s1.stage += lead_time;
    s1.s += b * int(ac.is_work == -1) - a * int(ac.is_work == 1);
    return std::pair<int, state>{lead_time, s1};
}



