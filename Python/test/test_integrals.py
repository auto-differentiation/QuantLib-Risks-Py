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

import QuantLib_Risks as ql
import unittest
if ql.XAD_ENABLED:
    from xad_autodiff import math
else:
    import math


class IntegralTest(unittest.TestCase):
    def Gauss(self, x):
        return math.exp(-x * x / 2.0) / math.sqrt(2 * math.pi)

    def singleTest(self, I):
        tolerance = 1e-4
        cases = [
            ["f(x) = 1", lambda x: 1, 0.0, 1.0, 1.0],
            ["f(x) = x", lambda x: x, 0.0, 1.0, 0.5],
            ["f(x) = x^2", lambda x: x * x, 0.0, 1.0, 1.0 / 3.0],
            ["f(x) = sin(x)", math.sin, 0.0, math.pi, 2.0],
            ["f(x) = cos(x)", math.cos, 0.0, math.pi, 0.0],
            ["f(x) = Gauss(x)", self.Gauss, -10.0, 10.0, 1.0],
        ]

        for tag, f, a, b, expected in cases:
            calculated = I(f, a, b)
            if not (abs(calculated - expected) <= tolerance):
                self.fail(
                    """
integrating %(tag)s
    calculated: %(calculated)f
    expected  : %(expected)f
                      """
                    % locals()
                )

    def testSegment(self):
        "Testing segment integration"
        self.singleTest(ql.SegmentIntegral(10000))

    def testTrapezoid(self):
        "Testing trapezoid integration"
        self.singleTest(ql.TrapezoidIntegralDefault(1.0e-4, 1000))

    def testSimpson(self):
        "Testing Simpson integration"
        self.singleTest(ql.SimpsonIntegral(1.0e-4, 1000))

    def testKronrod(self):
        "Testing Gauss-Kronrod integration"
        self.singleTest(ql.GaussKronrodAdaptive(1.0e-4))


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
