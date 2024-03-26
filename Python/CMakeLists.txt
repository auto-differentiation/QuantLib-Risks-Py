##############################################################################
#  Main CMake file for the Python extension.
#
#  This file is part of QuantLib-Risks, a Python wrapper for QuantLib enabled
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
if(NOT "${QLR_PYTHON_VERSION}" STREQUAL "")
  find_package (Python3 ${QLR_PYTHON_VERSION} EXACT COMPONENTS Interpreter Development.Module  REQUIRED)
else()
  find_package (Python3 COMPONENTS Interpreter Development.Module REQUIRED)
endif()

# fetch pybind11 dependency on the fly
include(FetchContent)

FetchContent_Declare(pybind11
            GIT_REPOSITORY   https://github.com/pybind/pybind11.git
            GIT_TAG          v2.11.1)
FetchContent_GetProperties(pybind11)
if(NOT pybind11_POPULATED)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
endif()

if(WIN32)
  set(QL_MODULE_SUFFIX ".${Python3_SOABI}.pyd")
else()
  set(QL_MODULE_SUFFIX ".${Python3_SOABI}${CMAKE_SHARED_MODULE_SUFFIX}")
endif()

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/build_extensions.py.in
               ${CMAKE_CURRENT_BINARY_DIR}/build_extensions.py @ONLY)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml.in
               ${CMAKE_CURRENT_BINARY_DIR}/pyproject.toml @ONLY)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/README.md
               ${CMAKE_CURRENT_BINARY_DIR}/README.md COPYONLY)


add_subdirectory(QuantLib_Risks)

