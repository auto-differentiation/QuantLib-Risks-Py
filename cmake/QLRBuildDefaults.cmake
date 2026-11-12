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

# Build settings for QuantLib and the extension module, as in QuantLibAAD's own build.
# Included before both, so they apply to the QuantLib build and to the module.

# no fused multiply-add contraction, so that AD values match plain double bit for bit;
# MSVC needs nothing: since VS 2022, /fp:precise only contracts with /fp:contract
if(CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$")
  if(CMAKE_CXX_COMPILER_FRONTEND_VARIANT STREQUAL "MSVC")
    add_compile_options(/clang:-ffp-contract=off)
  else()
    add_compile_options(-ffp-contract=off)
  endif()
endif()

# link-time optimisation of the static QuantLib and the module on Linux, so both must be built with
# the same compiler (GCC's or Clang's LTO objects hold only their IR); not on macOS and Windows.
# A CMAKE_INTERPROCEDURAL_OPTIMIZATION on the command line wins.
if(NOT DEFINED CMAKE_INTERPROCEDURAL_OPTIMIZATION AND CMAKE_SYSTEM_NAME STREQUAL "Linux"
   AND CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang)$")
  include(CheckIPOSupported)
  check_ipo_supported(RESULT qlr_ipo OUTPUT qlr_ipo_output LANGUAGES CXX)
  if(qlr_ipo)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
  else()
    message(WARNING "Link-time optimisation not supported, building without it: ${qlr_ipo_output}")
  endif()
endif()
