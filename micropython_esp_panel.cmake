# MicroPython USER_C_MODULES: mpy_support Python wrapper for ESP32_Display_Panel.
# ESP32_Display_Panel, esp-lib-utils, and ESP32_IO_Expander are IDF components
# registered via EXTRA_COMPONENT_DIRS in CMakeLists.txt.

add_library(usermod_esp_panel_mpy INTERFACE)

set(ESP_PANEL_DIR /home/lpinard/Repos/ESP32_Display_Panel)
set(MPY_DIR ${ESP_PANEL_DIR}/mpy_support)
file(GLOB MPY_C   ${MPY_DIR}/*.c)
file(GLOB MPY_CXX ${MPY_DIR}/*.cpp)

target_sources(usermod_esp_panel_mpy INTERFACE ${MPY_C} ${MPY_CXX})

# Include: mpy_support dir (has copied esp_lcd headers) + library source dir
target_include_directories(usermod_esp_panel_mpy INTERFACE
    ${MPY_DIR}
    ${ESP_PANEL_DIR}/src
    ${ESP_PANEL_DIR}
)

target_compile_options(usermod_esp_panel_mpy INTERFACE
    -Wno-missing-field-initializers -DESP_PLATFORM $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>
)

target_link_libraries(usermod INTERFACE usermod_esp_panel_mpy)
