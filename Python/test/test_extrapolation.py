"""
 Copyright (C) 2019 Klaus Spanderen
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

import unittest

import quantlib_risks as ql
if ql.XAD_ENABLED:
    from xad_autodiff import math
else:
    import math


class ExtrapolationTest(unittest.TestCase):
    def testKnownExpExtrapolation(self):
        """Testing Richardson extrapolation of e^x at x->1 with known order of convergence"""
        f = lambda x: math.exp(1+x)
        x = ql.RichardsonExtrapolation(f, 0.01, 1.0)(4.0)

        self.assertAlmostEqual(x, math.exp(1), 4,
            msg="Unable to extrapolate exp(x) at x->1")

    def testUnknownExpExtrapolation(self):
        """Testing Richardson extrapolation of e^x at x->1 with unknown order of convergence"""
        f = lambda x: math.exp(1+x)
        x = ql.RichardsonExtrapolation(f, 0.01)(4.0, 2.0)

        self.assertAlmostEqual(x, math.exp(1), 4,
            msg="Unable to extrapolate exp(x) at x->1")


if __name__ == "__main__":
    print("testing QuantLib", ql.__version__)
    unittest.main(verbosity=2)
