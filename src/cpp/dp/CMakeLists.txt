project(dp VERSION 0.0.1)
# third party
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

add_executable(dp_main main.cpp tail.cpp tail.h action.cpp action.h state.cpp state.h problem_queue.cpp problem_queue.h)
target_link_libraries(dp_main PRIVATE nlohmann_json::nlohmann_json)

add_executable(dp_test test.cpp tail.cpp tail.h action.cpp action.h state.cpp state.h problem_queue.cpp problem_queue.h)
target_link_libraries(dp_test PRIVATE nlohmann_json::nlohmann_json)