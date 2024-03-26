##############################################################################
#  Build SWIG binary module and optionally wheel package.
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

set_property(SOURCE ${PROJECT_SOURCE_DIR}/SWIG/quantlib.i PROPERTY CPLUSPLUS ON)
set_property(SOURCE ${PROJECT_SOURCE_DIR}/SWIG/quantlib.i PROPERTY USE_SWIG_DEPENDENCIES TRUE)
set_property(SOURCE ${PROJECT_SOURCE_DIR}/SWIG/quantlib.i PROPERTY COMPILE_OPTIONS -DQL_XAD=1)
swig_add_library(QuantLib_Risks
                 LANGUAGE python
                 OUTPUT_DIR .
                 SOURCES ${PROJECT_SOURCE_DIR}/SWIG/quantlib.i converters.cpp
)
target_link_libraries(QuantLib_Risks PRIVATE Python3::Module QuantLib::QuantLib pybind11::headers)
target_compile_features(QuantLib_Risks PRIVATE c_std_17)
target_compile_definitions(QuantLib_Risks PRIVATE QL_XAD=1)
target_include_directories(QuantLib_Risks PRIVATE .)
set_property(TARGET QuantLib_Risks PROPERTY SUFFIX "${QL_MODULE_SUFFIX}")
if(MSVC)
    # we build with the static runtime in Windows
    set_target_properties(QuantLib_Risks PROPERTIES 
            MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/__init__.py
               ${CMAKE_CURRENT_BINARY_DIR}/__init__.py COPYONLY)

if(WIN32)
    set(VENV_PYTHON ${CMAKE_CURRENT_BINARY_DIR}/../.venv/Scripts/python.exe)
else()
    set(VENV_PYTHON ${CMAKE_CURRENT_BINARY_DIR}/../.venv/bin/python)
endif()

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/../wheel.stamp
    DEPENDS QuantLib_Risks
            ${CMAKE_CURRENT_BINARY_DIR}/../pyproject.toml
            ${CMAKE_CURRENT_BINARY_DIR}/../build_extensions.py
            ${CMAKE_CURRENT_BINARY_DIR}/../README.md
            __init__.py
    # create environment
    COMMAND ${Python3_EXECUTABLE} -m venv .venv
    # install build dependencies
    COMMAND ${VENV_PYTHON} -m pip install -U pip setuptools wheel build
    # build the wheel
    COMMAND ${VENV_PYTHON} -m pip wheel .
    # install the wheel in the venv
    COMMAND ${VENV_PYTHON} -m pip install QuantLib_Risks*.whl --force-reinstall
    # install other dependencies for running the examples / tests
    COMMAND ${VENV_PYTHON} -m pip install -r ${PROJECT_SOURCE_DIR}/binder/requirements.txt
    # update the stamp file, to keep track of when we last build it
    COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_CURRENT_BINARY_DIR}/../wheel.stamp
    COMMENT "Building Python wheel..."
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/..
)

# main target for building the python wheel - custom command above will be hooked to this target
add_custom_target(python_wheel 
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/../wheel.stamp)

