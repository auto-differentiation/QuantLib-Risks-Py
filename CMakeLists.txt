##############################################################################
#   CMake file for QuantLib-Risks. The version set here is used for the Python
#   package.
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

cmake_minimum_required(VERSION 3.15.0)
project(QuantLib_Risks LANGUAGES CXX VERSION 1.33.3)

# For MSVC RUNTIME LIBRARY, need CMP0091=NEW and cmake 3.15+
cmake_policy(SET CMP0091 NEW)
set(PACKAGE_VERSION       "${PROJECT_VERSION}")
set(PACKAGE_VERSION_HEX   "0x013303f0")
set(QLR_VERSION ${PACKAGE_VERSION})
set(QLR_HEX_VERSION ${PACKAGE_VERSION_HEX})


find_package(QuantLib-Risks REQUIRED)
find_package(SWIG REQUIRED)

include(UseSWIG)

enable_testing()


add_subdirectory(Python)
