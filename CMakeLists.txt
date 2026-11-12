##############################################################################
#   CMake file for QuantLibAAD, driven by scikit-build-core (pyproject.toml).
#   Keep the version in sync with pyproject.toml.
#
#  This file is part of QuantLibAAD, a Python wrapper for QuantLib enabled
#  for risk computation using automatic differentiation. It uses XAD,
#  a fast and comprehensive C++ library for automatic differentiation.
#
#  Copyright (C) 2010-2024 Xcelerit Computing Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

cmake_minimum_required(VERSION 3.18...4.2)
project(QuantLibAAD_Py LANGUAGES CXX VERSION 1.44.0)

set(QLR_VERSION ${PROJECT_VERSION})
set(QLR_HEX_VERSION "0x014400f0")

if(NOT DEFINED CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# dynamic MSVC runtime everywhere (QuantLib, the module), as libxad is a DLL
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")

option(QLR_QUANTLIB_ONLY
       "Only build and install QuantLib + QuantLibAAD, for reuse via QLR_QUANTLIB_PREFIX"
       OFF)
set(QLR_QUANTLIB_PREFIX "" CACHE PATH
    "Install prefix of a QLR_QUANTLIB_ONLY build to reuse (empty: build QuantLib from lib/)")

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")

include(QLRBuildDefaults)
include(QLRXad)

if(QLR_QUANTLIB_PREFIX AND NOT QLR_QUANTLIB_ONLY)
  include(PrebuiltQuantLib)
else()
  include(QuantLibFromSource)
endif()

if(NOT QLR_QUANTLIB_ONLY)
  add_subdirectory(Python)
endif()
