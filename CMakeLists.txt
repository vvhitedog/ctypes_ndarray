cmake_minimum_required(VERSION 3.1)
project(ctypes-ndarray)

set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 0)
set(PROJECT_VERSION_PATCH 1)
set(PROJECT_VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH} )
set(PROJECT_AUTHOR Matt Gara )
set(PROJECT_AUTHOR_EMAIL gara.matt@gmail.com )
set(PROJECT_DESCRIPTION "A simple interface to use numpy.ndarray in C++ or C code, allowing python to hold ownership at all times.")

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_VERBOSE_MAKEFILE on)

include(GNUInstallDirs)

set(SRCS src/NdArray.cpp)
set(HEADERS src/NdArray.h)
add_library(cndarray SHARED ${SRCS} ${HEADERS})

# Install setup:
set_target_properties(cndarray PROPERTIES
  VERSION ${PROJECT_VERSION}
  SOVERSION ${PROJECT_VERSION_MAJOR}
  PUBLIC_HEADER "${HEADERS}")
install(TARGETS cndarray
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/cndarray )
