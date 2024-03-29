# settings
set(ANACONDA_PYTHON_VERBOSE ON)
set(CPPREPAIRDP_INCLUDE_DIR "${PROJECT_SOURCE_DIR}/cpp/dp")
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})
# packages
find_package(SWIG REQUIRED)
include_directories(${SWIG_INCLUDE_DIR})
include(${SWIG_USE_FILE})
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})
include(FindConda)

message(NOTICE "PYTHON INCLUDE: ${PYTHON_INCLUDE_DIRS}")
message(NOTICE "CPPREPAIR-DP INCLUDE: ${CPPREPAIRDP_INCLUDE_DIR}")

# PURE CPP (TEST PATHS etc.)
add_executable(dp_py main.cpp)

target_include_directories(dp_py PUBLIC ${CPPREPAIRDP_INCLUDE_DIR} ${EIGEN} "${PROJECT_BINARY_DIR}")
target_link_libraries(dp_py PRIVATE nlohmann_json::nlohmann_json )
target_link_libraries(dp_py PRIVATE cpprepairdp)

# SWIG PYTHON LIB
set_property(SOURCE dp.i PROPERTY CPLUSPLUS ON)
set_property(SOURCE dp.i PROPERTY SWIG_MODULE_NAME pydp)

swig_add_library(pydp
        TYPE SHARED
        LANGUAGE python
        SOURCES dp.i)

target_include_directories(
        pydp
        PRIVATE
        ${CPPREPAIRDP_INCLUDE_DIR}
        ${PYTHON_INCLUDE_DIRS}
        ${PROJECT_BINARY_DIR}
)

target_link_libraries(
        pydp
        PRIVATE
        ${PYTHON_LIBRARY}
        cpprepairdp
        nlohmann_json::nlohmann_json
)

set_property(TARGET pydp PROPERTY SWIG_USE_TARGET_INCLUDE_DIRECTORIES ON)

# note: macOS is APPLE and also UNIX !
if(APPLE)
    set_target_properties(pydp PROPERTIES
            SUFFIX ".so"
            INSTALL_RPATH "@loader_path;@loader_path./"
            )
    set_property(TARGET pydp APPEND PROPERTY
            LINK_FLAGS "-flat_namespace -undefined suppress"
            )
elseif(UNIX)
    set_target_properties(pyFoo PROPERTIES
            INSTALL_RPATH "$ORIGIN:$ORIGIN/"
            )
endif()


# Variable PYTHON_LIBRARIES can contains keyword `optimized`
# which won't be interpreted inside a generator expression.
# i.e. we can't use: $<$<PLATFORM_ID:Windows>:${PYTHON_LIBRARIES}>
# see: https://cmake.org/cmake/help/git-stage/command/target_link_libraries.html#command:target_link_libraries

