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

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

python "${SCRIPT_DIR}/test/QuantLibTestSuite.py"

cd "${SCRIPT_DIR}/examples"

had_errors=0
for f in "swap-adjoint.py" "swap.py" "multicurve-bootstrapping.py" ; do
    echo ""
    echo "----------- RUNNING $f ----------------"
    python "$f" || had_errors=1
done

if [ "$had_errors" == "1" ] ; then
    echo "there were errors"
    exit 1
fi
