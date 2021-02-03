
add_library(mip mip.cpp mosek_mip.cpp)
add_executable(mip_grb_single gurobi_single_mip.cpp)
# add modules
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})
# gurobi
find_package(GUROBI REQUIRED)
include_directories(${GUROBI_INCLUDE_DIRS})

target_link_libraries(mip_grb_single ${GUROBI_CXX_LIBRARY})
target_link_libraries(mip_grb_single ${GUROBI_LIBRARY})

