
cmake_minimum_required(VERSION 3.15)


# set the project name
project(dualnewsvendor VERSION 0.0.1 LANGUAGES C CXX)
# specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)



# add subdirectories
add_subdirectory(cpp)
add_subdirectory(thirdparty)
add_subdirectory(python)