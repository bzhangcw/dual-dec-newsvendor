//
// Created by C. Zhang on 2021/2/3.
//

#include "tail.h"
#include <string>

tail_counter tc = tail_counter();

tail::~tail() {};

tail::tail(state &st, action &ac) {
    this->st = state(st);
    this->ac = action(ac);
    this->id = tc.number;
    tc.number += 1;
    this->key = this->to_string();
};

std::string tail::to_string() {
    return this->ac.to_string() + "," + this->st.to_string();
}