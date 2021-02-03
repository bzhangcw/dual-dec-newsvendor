# CMake generated Testfile for 
# Source directory: /Users/brent/Archiver/Workspace/repair/src/cpp
# Build directory: /Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(Comp4 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "4")
set_tests_properties(Comp4 PROPERTIES  PASS_REGULAR_EXPRESSION "4 is 2" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;45;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
add_test(Comp9 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "9")
set_tests_properties(Comp9 PROPERTIES  PASS_REGULAR_EXPRESSION "9 is 3" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;46;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
add_test(Comp5 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "5")
set_tests_properties(Comp5 PROPERTIES  PASS_REGULAR_EXPRESSION "5 is 2.236" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;47;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
add_test(Comp7 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "7")
set_tests_properties(Comp7 PROPERTIES  PASS_REGULAR_EXPRESSION "7 is 2.645" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;48;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
add_test(Comp25 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "25")
set_tests_properties(Comp25 PROPERTIES  PASS_REGULAR_EXPRESSION "25 is 5" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;49;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
add_test(Comp-25 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "-25")
set_tests_properties(Comp-25 PROPERTIES  PASS_REGULAR_EXPRESSION "-25 is [-nan|nan|0]" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;50;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
add_test(Comp0.0001 "/Users/brent/Archiver/Workspace/repair/src/cpp/cmake-build-debug/try" "0.0001")
set_tests_properties(Comp0.0001 PROPERTIES  PASS_REGULAR_EXPRESSION "0.0001 is 0.01" _BACKTRACE_TRIPLES "/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;38;add_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;51;do_test;/Users/brent/Archiver/Workspace/repair/src/cpp/CMakeLists.txt;0;")
subdirs("aq")
subdirs("mip")
