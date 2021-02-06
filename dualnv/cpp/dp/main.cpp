#include "dp.h"

int main(int argc, char *argv[]) {
    using namespace std;
    bool bool_option = (string(argv[2]) == "T");
    run_test(argv[1], bool_option);
    return 1;
}
