#!/bin/bash

##############################################################################
#   
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

# exit on errors immediately
set -e

if [ "$CMAKE_INSTALL_PREFIX" == "" ] ; then
    export CMAKE_INSTALL_PREFIX=$(pwd)/build/prefix
fi

if [ "$QL_PRESET" == "" ] ; then
    export QL_PRESET=linux-xad-gcc-ninja-release
fi

if [ "$CCACHE_EXE" != "" ] ; then
    export CCACHE_OPTION="-DCMAKE_CXX_COMPILER_LAUNCHER=$CCACHE_EXE"
fi

if [ "$QLR_PYTHON_VERSION" == "cp38" ] ; then
  export PYTHON_OPTION="-DQLR_PYTHON_VERSION=3.8"
elif [ "$QLR_PYTHON_VERSION" == "cp39" ] ; then
  export PYTHON_OPTION="-DQLR_PYTHON_VERSION=3.9"
elif [ "$QLR_PYTHON_VERSION" == "cp310" ] ; then
  export PYTHON_OPTION="-DQLR_PYTHON_VERSION=3.10"
elif [ "$QLR_PYTHON_VERSION" == "cp311" ] ; then
  export PYTHON_OPTION="-DQLR_PYTHON_VERSION=3.11"
elif [ "$QLR_PYTHON_VERSION" == "cp312" ] ; then
  export PYTHON_OPTION="-DQLR_PYTHON_VERSION=3.12"
fi

export QL_DIR=$(pwd)/lib/QuantLib
export QLXAD_DIR=$(pwd)/lib/quantlib-xad
export XAD_DIR=$(pwd)/lib/XAD
export QLSWIG_DIR=$(pwd)

echo "Step 0: Package setup"
case "$(uname -sr)" in
   Darwin*)
     machine="macos"
     ;;

   Linux*Microsoft*)
     machine="linux"
     ;;

   Linux*)
     machine="linux"
     ;;

   CYGWIN*|MINGW*|MINGW32*|MSYS*)
     machine="windows"
     ;;

   *)
     echo 'Other OS' 
     exit 1
     ;;
esac

if [ "$machine" == "linux" ] ; then
    # Linux builds in a container, so we need to install boost there
    curl -O -L https://boostorg.jfrog.io/artifactory/main/release/1.84.0/source/boost_1_84_0.tar.gz
    tar xfz boost_*.tar.gz
    cd boost_*/
    mv boost /usr/local/include/
    cd ..

    if which yum ; then
        yum -y install ninja-build ccache
    else 
        apk add --no-cache ninja ccache
    fi

    export CCACHE_OPTION="-DCMAKE_CXX_COMPILER_LAUNCHER=ccache"
    ccache -o cache_dir="/host$HOST_CCACHE_DIR"
fi

echo "Step 1: Build QuantLib with XAD support"
cd "$QL_DIR"
# this is required in v1.33 - remove after moving to 1.34
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"
git log | grep -q "Uses Real in GemoetricBrownianMotionProcess instead of double" || (git fetch --all && git cherry-pick 6bb9c1f18ff6d4c47f06a66136fb83411207e67c)
if [ "$machine" != "macos" ] ; then
    cp -f "$QLXAD_DIR/presets/CMakeUserPresets.json" .
    cmake --preset "$QL_PRESET" \
    -DCMAKE_INSTALL_PREFIX="$CMAKE_INSTALL_PREFIX" \
    -DXAD_ENABLE_TESTS=OFF \
    -DQL_BUILD_TEST_SUITE=OFF \
    -DQL_BUILD_EXAMPLES=OFF \
    -DQL_BUILD_BENCHMARK=OFF \
    $CCACHE_OPTION
else 
    # we don't have working presets for Intel Mac
    mkdir -p build/$QL_PRESET
    cmake -B build/$QL_PRESET -S . -GNinja \
      -DCMAKE_INSTALL_PREFIX="$CMAKE_INSTALL_PREFIX" \
      -DXAD_ENABLE_TESTS=OFF \
      -DQL_BUILD_TEST_SUITE=OFF \
      -DQL_BUILD_EXAMPLES=OFF \
      -DQL_BUILD_BENCHMARK=OFF \
      $CCACHE_OPTION \
      -DCMAKE_BUILD_TYPE=Release \
      -DQLXAD_DISABLE_AAD=OFF \
      -DQL_EXTERNAL_SUBDIRECTORIES="$XAD_DIR;$QLXAD_DIR" \
      -DQL_EXTRA_LINK_LIBRARIES="quantlib-xad" \
      -DQL_NULL_AS_FUNCTIONS=ON \
      -DXAD_NO_THREADLOCAL=ON 
fi

cd "build/$QL_PRESET"
cmake --build .
cmake --install .

echo "Step 2: Build QuantLib-SWIG"
cd "$QLSWIG_DIR"
mkdir -p "build/$QL_PRESET"
cd "build/$QL_PRESET"
cmake -G Ninja ../.. \
    -DCMAKE_INSTALL_PREFIX="$CMAKE_INSTALL_PREFIX"  \
    -DCMAKE_BUILD_TYPE=Release \
    $CCACHE_OPTION $PYTHON_OPTION
cmake --build . 

echo "Now ready to build the pypi package in $QLSWIG_DIR/build/$QL_PRESET/Python ..."





