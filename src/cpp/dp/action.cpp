//
// Created by C. Zhang on 2021/2/4.
//

#include "action.h"
#include <iostream>

action::~action() {};

action::action(int action) {
    this->is_work = action;
};

action::action(const action &action) {
    *this = action;
}

std::string action::to_string() {
    return std::to_string(this->is_work);
}