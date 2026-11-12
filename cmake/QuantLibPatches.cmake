##############################################################################
#  Copies the QuantLib source in QUANTLIB_SOURCE_DIR to QUANTLIB_PATCHED_DIR
#  and applies the temporary QuantLib fixes in patches/quantlib to the copy,
#  which is then configured instead. A patch that doesn't fit stops the build.
#  Included by QuantLibFromSource, or run alone:
#
#    cmake -DQUANTLIB_SOURCE_DIR=<dir> -DQUANTLIB_PATCHED_DIR=<dir> -P cmake/QuantLibPatches.cmake
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

foreach(var QUANTLIB_SOURCE_DIR QUANTLIB_PATCHED_DIR)
  if(NOT ${var})
    message(FATAL_ERROR "${var} is not set")
  endif()
endforeach()
find_package(Git REQUIRED)
file(GLOB qlr_patches "${CMAKE_CURRENT_LIST_DIR}/../patches/quantlib/*.patch")
list(SORT qlr_patches)

# without .git, which may be a submodule's link to a repository that isn't there (an sdist)
file(COPY "${QUANTLIB_SOURCE_DIR}/" DESTINATION "${QUANTLIB_PATCHED_DIR}" PATTERN ".git" EXCLUDE)
# file(COPY) keeps a destination that is newer, as the files patched last time are
foreach(patch IN LISTS qlr_patches)
  file(STRINGS "${patch}" targets REGEX "^\\+\\+\\+ b/")
  foreach(target IN LISTS targets)
    string(REGEX REPLACE "^\\+\\+\\+ b/" "" rel "${target}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy "${QUANTLIB_SOURCE_DIR}/${rel}"
                                                     "${QUANTLIB_PATCHED_DIR}/${rel}"
                    RESULT_VARIABLE rc)
    if(NOT rc EQUAL 0)
      message(FATAL_ERROR "cannot copy ${rel} from ${QUANTLIB_SOURCE_DIR} for patch ${patch}")
    endif()
  endforeach()
endforeach()

# git apply works relative to the enclosing repository: stop it from looking above the copy
# (e.g. a build directory inside another checkout)
get_filename_component(qlr_ceiling "${QUANTLIB_PATCHED_DIR}" DIRECTORY)
set(qlr_git ${CMAKE_COMMAND} -E env "GIT_CEILING_DIRECTORIES=${qlr_ceiling}" "${GIT_EXECUTABLE}")

foreach(patch IN LISTS qlr_patches)
  get_filename_component(name "${patch}" NAME)
  execute_process(COMMAND ${qlr_git} apply "${patch}"
                  WORKING_DIRECTORY "${QUANTLIB_PATCHED_DIR}"
                  RESULT_VARIABLE rc ERROR_VARIABLE err)
  if(NOT rc EQUAL 0)
    message(FATAL_ERROR "QuantLib patch ${name} does not apply to ${QUANTLIB_SOURCE_DIR}:\n${err}")
  endif()
  message(STATUS "QuantLib patch applied: ${name}")
endforeach()
