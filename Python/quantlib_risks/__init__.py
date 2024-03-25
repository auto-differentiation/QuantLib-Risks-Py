# -*- coding: iso-8859-1 -*-
"""
 Copyright (C) 2000, 2001, 2002, 2003 RiskMap srl
 Copyright (C) 2024 Xcelerit Computing Limited.

 This file is part of quantlib-risks, a Python wrapper for QuantLib enabled
 for risk computation using automatic differentiation. It uses XAD,
 a fast and comprehensive C++ library for automatic differentiation.

 quantlib-risks and XAD are free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 quantlib-risks is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 QuantLib is free software: you can redistribute it and/or modify it
 under the terms of the QuantLib license.  You should have received a
 copy of the license along with this program; if not, please email
 <quantlib-dev@lists.sf.net>. The license is also available online at
 <http://quantlib.org/license.shtml>.

 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
"""

from .quantlib_risks import *

if XAD_ENABLED:
    from xad_autodiff.adj_1st import Real
    from typing import Union, Tuple, List

    # as part of the input at the top, we'll have _quantlib_risks in scope
    DoubleVector = _quantlib_risks.DoubleVector
    DoublePairVector = _quantlib_risks.DoublePairVector
    DoubleVectorVector = _quantlib_risks.DoubleVectorVector

    def Concentrating1dMesherPoint(x1: Union[Real, float, int], x2: Union[Real, float, int], v: bool) -> Tuple[Real, Real, bool]:
        return (Real(x1), Real(x2), bool(v))

    def PairDoubleVector(x1: List[Union[Real, float, int]] = [], x2: List[Union[Real, float, int]] = []) -> Tuple[List[Real], List[Real]]:
        return ([Real(x) for x in x1], [Real(x) for x in x2])

if hasattr(_quantlib_risks,'__version__'):
    __version__ = _quantlib_risks.__version__
elif hasattr(_quantlib_risks.cvar,'__version__'):
    __version__ = _quantlib_risks.cvar.__version__
else:
    print('Could not find __version__ attribute')

if hasattr(_quantlib_risks,'__hexversion__'):
    __hexversion__ = _quantlib_risks.__hexversion__
elif hasattr(_quantlib_risks.cvar,'__hexversion__'):
    __hexversion__ = _quantlib_risks.cvar.__hexversion__
else:
    print('Could not find __hexversion__ attribute')
