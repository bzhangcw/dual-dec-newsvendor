find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

# add the executable
add_executable(try try.cpp)

# add subdirectories
# == null object: for fun ===
add_subdirectory(aq)
# == mip ===
add_subdirectory(mip)
# == dp ===
add_subdirectory(dp)


# link libraries
list(APPEND EXTRA_LIBS aq mip)
list(APPEND EXTRA_INCLUDES "${PROJECT_SOURCE_DIR}/aq;${PROJECT_SOURCE_DIR}/mip")

target_link_libraries(try PUBLIC ${EXTRA_LIBS})

# add include
target_include_directories(
        try PUBLIC
        "${PROJECT_BINARY_DIR}"
        ${EXTRA_INCLUDES}
)

# testing
enable_testing()

# define a function to simplify adding tests
function(do_test target arg result)
    add_test(NAME Comp${arg} COMMAND ${target} ${arg})
    set_tests_properties(Comp${arg}
            PROPERTIES PASS_REGULAR_EXPRESSION ${result}
            )
endfunction(do_test)

# do a bunch of result based tests
do_test(try 4 "4 is 2")
do_test(try 9 "9 is 3")
do_test(try 5 "5 is 2.236")
do_test(try 7 "7 is 2.645")
do_test(try 25 "25 is 5")
do_test(try -25 "-25 is [-nan|nan|0]")
do_test(try 0.0001 "0.0001 is 0.01")