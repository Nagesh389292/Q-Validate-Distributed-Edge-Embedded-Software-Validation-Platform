cmake_minimum_required(VERSION 3.16)
project(qvalidate_device_runtime CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

file(GLOB SOURCES "src/*.cpp")

add_executable(qvalidate_device_runtime ${SOURCES})

if (MSVC)
    target_compile_options(qvalidate_device_runtime PRIVATE /W4 /EHsc)
else()
    target_compile_options(qvalidate_device_runtime PRIVATE -Wall -Wextra -O2)
endif()
