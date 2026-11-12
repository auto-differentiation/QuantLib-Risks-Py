##############################################################################
#  Applies the temporary QuantLib fixes in patches/quantlib to the QuantLib
#  source in QUANTLIB_SOURCE_DIR, before it is configured. A patch already
#  applied is skipped; one that doesn't fit stops the build. Included by
#  QuantLibFromSource, or run alone:
#
#    cmake -DQUANTLIB_SOURCE_DIR=<dir> -P cmake/QuantLibPatches.cmake
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

if(NOT QUANTLIB_SOURCE_DIR)
  message(FATAL_ERROR "QUANTLIB_SOURCE_DIR is not set")
endif()
find_package(Git REQUIRED)
file(GLOB qlr_patches "${CMAKE_CURRENT_LIST_DIR}/../patches/quantlib/*.patch")
list(SORT qlr_patches)

# git apply works relative to the enclosing repository: stop it from looking above the
# QuantLib source (e.g. a source tree unpacked inside another checkout)
get_filename_component(qlr_ceiling "${QUANTLIB_SOURCE_DIR}" DIRECTORY)
set(qlr_git ${CMAKE_COMMAND} -E env "GIT_CEILING_DIRECTORIES=${qlr_ceiling}" "${GIT_EXECUTABLE}")

foreach(patch IN LISTS qlr_patches)
  get_filename_component(name "${patch}" NAME)
  execute_process(COMMAND ${qlr_git} apply --check --reverse "${patch}"
                  WORKING_DIRECTORY "${QUANTLIB_SOURCE_DIR}"
                  RESULT_VARIABLE already_applied OUTPUT_QUIET ERROR_QUIET)
  if(already_applied EQUAL 0)
    message(STATUS "QuantLib patch already applied: ${name}")
    continue()
  endif()
  execute_process(COMMAND ${qlr_git} apply "${patch}"
                  WORKING_DIRECTORY "${QUANTLIB_SOURCE_DIR}"
                  RESULT_VARIABLE rc ERROR_VARIABLE err)
  if(NOT rc EQUAL 0)
    message(FATAL_ERROR "QuantLib patch ${name} does not apply to ${QUANTLIB_SOURCE_DIR}:\n${err}")
  endif()
  message(STATUS "QuantLib patch applied: ${name}")
endforeach()
