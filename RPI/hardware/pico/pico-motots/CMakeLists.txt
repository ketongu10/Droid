cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(test_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_executable(test
  test.c
)

#pico_enable_stdio_usb(test 1)
#pico_enable_stdio_uart(test 1)

pico_add_extra_outputs(test)

target_link_libraries(test 
pico_i2c_slave
hardware_i2c
hardware_adc
hardware_pwm
pico_stdlib
)
