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

std::string state::to_string() {
    return std::to_string(this->stage) + "," + std::to_string(this->s);
}

bool operator==(const state &lhs, const state &rhs) {
    return lhs.s == rhs.s && lhs.stage == rhs.stage;
}

double state::evaluate() {
    return 0;
}

