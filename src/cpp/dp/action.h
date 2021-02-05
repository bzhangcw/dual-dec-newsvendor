//
// Created by C. Zhang on 2021/2/4.
//

#ifndef REPAIRCPP_ACTION_H
#define REPAIRCPP_ACTION_H

#include <iostream>

class action {
public:
    int is_work{};

    action() { this->is_work = 1; };

    explicit action(int action);

    action(action const &action);
    std::string to_string() const ;
    ~action();
    double evaluate(double multiplier);
};


#endif //REPAIRCPP_ACTION_H
