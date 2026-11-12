##############################################################################
#
#  This file is part of QuantLibAAD, a Python wrapper for QuantLib enabled
#  for risk computation using automatic differentiation. It uses XAD,
#  a fast and comprehensive C++ library for automatic differentiation.
#
#  Copyright (C) 2010-2026 Xcelerit Computing Ltd.
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

# XAD from the installed xad Python package (shared libxad, tape shared with xad-py).
# XAD_DIR overrides the package lookup. Defines XAD::xad.

if(NOT XAD_DIR)
  find_package(Python 3.10 REQUIRED COMPONENTS Interpreter)
  execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import xad; print(xad.get_cmake_dir())"
    OUTPUT_VARIABLE xad_cmake_dir OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE xad_rc)
  if(NOT xad_rc EQUAL 0)
    message(FATAL_ERROR "xad not importable by ${Python_EXECUTABLE}: pip install \"xad>=2.2,<2.3\"")
  endif()
  file(TO_CMAKE_PATH "${xad_cmake_dir}" xad_cmake_dir)
  set(XAD_DIR "${xad_cmake_dir}" CACHE PATH "XAD CMake package directory" FORCE)
endif()

find_package(XAD 2.2 CONFIG REQUIRED)
if(XAD_VERSION VERSION_GREATER_EQUAL 2.3 OR NOT XAD_SHARED_LIBS OR XAD_NO_THREADLOCAL)
  message(FATAL_ERROR "XAD ${XAD_VERSION} in ${XAD_DIR}: need xad with shared libxad and "
                      "thread-local tapes")
endif()
message(STATUS "XAD ${XAD_VERSION}: ${XAD_DIR}")
