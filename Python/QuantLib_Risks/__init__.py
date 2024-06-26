# -*- coding: iso-8859-1 -*-
"""
 Copyright (C) 2000, 2001, 2002, 2003 RiskMap srl
 Copyright (C) 2024 Xcelerit Computing Limited.

 This file is part of QuantLib-Risks, a Python wrapper for QuantLib enabled
 for risk computation using automatic differentiation. It uses XAD,
 a fast and comprehensive C++ library for automatic differentiation.

 QuantLib-Risks and XAD are free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 QuantLib-Risks is distributed in the hope that it will be useful,
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

from .QuantLib_Risks import *

if XAD_ENABLED:
    from xad.adj_1st import Real, Tape
    from typing import Union, Tuple, List

    # as part of the input at the top, we'll have _QuantLib_Risks in scope
    DoubleVector = _QuantLib_Risks.DoubleVector
    DoublePairVector = _QuantLib_Risks.DoublePairVector
    DoubleVectorVector = _QuantLib_Risks.DoubleVectorVector

    def Concentrating1dMesherPoint(
        x1: Union[Real, float, int], x2: Union[Real, float, int], v: bool
    ) -> Tuple[Real, Real, bool]:
        return (Real(x1), Real(x2), bool(v))

    def PairDoubleVector(
        x1: List[Union[Real, float, int]] = [], x2: List[Union[Real, float, int]] = []
    ) -> Tuple[List[Real], List[Real]]:
        return ([Real(x) for x in x1], [Real(x) for x in x2])

    # monkey-patch the tape activation function to register this tape with QuantLib's internal
    # global tape pointer (we have 2 due to double static linking)
    def _wrap_tape_activation():
        original_enter = Tape.__enter__

        def _tape_enter(t: Tape):
            t = original_enter(t)
            _QuantLib_Risks._activate_tape(t)
            return t

        original_exit = Tape.__exit__

        def _tape_exit(t: Tape, *args, **kwargs):
            original_exit(t, *args, **kwargs)
            _QuantLib_Risks._deactivate_tape()

        original_activate = Tape.activate

        def _tape_activate(t: Tape):
            original_activate(t)
            _QuantLib_Risks._activate_tape(t)

        original_deactivate = Tape.deactivate

        def _tape_deactivate(t: Tape):
            original_deactivate(t)
            _QuantLib_Risks._deactivate_tape()

        Tape.__enter__ = _tape_enter
        Tape.__exit__ = _tape_exit
        Tape.activate = _tape_activate
        Tape.deactivate = _tape_deactivate

    _wrap_tape_activation()

if hasattr(_QuantLib_Risks, "__version__"):
    __version__ = _QuantLib_Risks.__version__
elif hasattr(_QuantLib_Risks.cvar, "__version__"):
    __version__ = _QuantLib_Risks.cvar.__version__
else:
    print("Could not find __version__ attribute")

if hasattr(_QuantLib_Risks, "__hexversion__"):
    __hexversion__ = _QuantLib_Risks.__hexversion__
elif hasattr(_QuantLib_Risks.cvar, "__hexversion__"):
    __hexversion__ = _QuantLib_Risks.cvar.__hexversion__
else:
    print("Could not find __hexversion__ attribute")
