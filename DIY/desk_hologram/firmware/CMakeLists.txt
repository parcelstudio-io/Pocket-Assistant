cmake_minimum_required(VERSION 3.16)
# Desk hologram firmware for the ESP32-C3 SuperMini: text in a beam-splitter cube.
# Ported from pocket_ai_assistant/character/firmware (the first Pocket AI) on 2026-11-01.
set(EXTRA_COMPONENT_DIRS "")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(desk_hologram)
